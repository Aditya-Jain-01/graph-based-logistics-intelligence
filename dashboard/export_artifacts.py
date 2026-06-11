import os
import json
import warnings
import pandas as pd
import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data
from sklearn.preprocessing import StandardScaler
from node2vec import Node2Vec
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib

warnings.filterwarnings("ignore")

# Configuration
DATA_FILE = "delivery_data.csv"
ARTIFACTS_DIR = "artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("🚀 Starting Offline Artifact Extraction Pipeline")

# ==========================================
# STAGE 1-5: Data Loading & Preprocessing
# ==========================================
print("📦 Loading dataset...")
df = pd.read_csv(DATA_FILE)

df = df[df["segment_factor"] > 0]
df = df[df["segment_factor"] <= 10]
df["source_name"]      = df["source_name"].fillna(df["source_center"])
df["destination_name"] = df["destination_name"].fillna(df["destination_center"])
df["od_start_time"]    = pd.to_datetime(df["od_start_time"], errors="coerce")

df["departure_hour"]        = df["od_start_time"].dt.hour.fillna(12).astype(int)
df["departure_day_of_week"] = df["od_start_time"].dt.dayofweek.fillna(2).astype(int)
df["hour_sin"]              = np.sin(2*np.pi*df["departure_hour"]/24)
df["hour_cos"]              = np.cos(2*np.pi*df["departure_hour"]/24)
df["is_night_shipment"]     = ((df["departure_hour"] < 6) | (df["departure_hour"] >= 22)).astype(int)
df["is_weekend"]            = (df["departure_day_of_week"] >= 5).astype(int)
df["is_delayed"]            = (df["segment_factor"] > 1.2).astype(int)
df["route_type_encoded"]    = (df["route_type"] == "FTL").astype(int)
df["is_cutoff"]             = df["is_cutoff"].astype(int)
df["osrm_speed_kmh"]        = np.where(
    df["segment_osrm_time"] > 0,
    df["segment_osrm_distance"] / (df["segment_osrm_time"] / 60),
    np.nan,
)

def _tod(h):
    if 6  <= h < 12: return "Morning"
    if 12 <= h < 18: return "Afternoon"
    if 18 <= h < 22: return "Evening"
    return "Night"
df["time_of_day"] = df["departure_hour"].apply(_tod)
df["corridor_id"] = df["source_center"] + "_" + df["destination_center"] + "_" + df["route_type"]

train_mask = df["data"] == "training"
test_mask  = df["data"] == "test"
cols_drop  = ["data","route_schedule_uuid","source_name","destination_name",
              "cutoff_timestamp","od_end_time","actual_time","factor",
              "start_scan_to_end_scan","osrm_time"]
df_model = df.drop(columns=[c for c in cols_drop if c in df.columns])
df_train = df_model[train_mask].reset_index(drop=True)
df_test  = df_model[test_mask].reset_index(drop=True)

corridor_stats = (
    df_train.groupby("corridor_id")
            .agg(corridor_median_delay=("segment_factor", "median"),
                 corridor_mean_delay  =("segment_factor", "mean"),
                 corridor_delay_std   =("segment_factor", "std"),
                 corridor_trip_volume =("trip_uuid", "nunique"),
                 corridor_pct_delayed =("is_delayed", "mean"))
            .reset_index()
)
df_train = df_train.merge(corridor_stats, on="corridor_id", how="left")
df_test  = df_test.merge(corridor_stats,  on="corridor_id", how="left")
for c in ["corridor_median_delay","corridor_mean_delay",
          "corridor_pct_delayed","corridor_delay_std"]:
    df_test[c] = df_test[c].fillna(df_train[c].median())
df_test["corridor_trip_volume"] = df_test["corridor_trip_volume"].fillna(0)


# ==========================================
# STAGE 6: Graph Construction
# ==========================================
print("🕸️ Building Graph...")
od_stats = (
    df_train
    .groupby(["source_center","destination_center"])
    .agg(median_delay = ("segment_factor",      "median"),
         mean_delay   = ("segment_factor",      "mean"),
         std_delay    = ("segment_factor",      "std"),
         pct_delayed  = ("is_delayed",          "mean"),
         trip_volume  = ("trip_uuid",           "nunique"),
         avg_minutes  = ("segment_actual_time", "mean"))
    .reset_index()
)
G = nx.DiGraph()
for _, row in od_stats.iterrows():
    G.add_edge(
        row["source_center"], row["destination_center"],
        weight        = float(row["median_delay"]),
        mean_delay    = float(row["mean_delay"]),
        delay_std     = 0.0 if np.isnan(row["std_delay"]) else float(row["std_delay"]),
        pct_delayed   = float(row["pct_delayed"]),
        trip_volume   = int(row["trip_volume"]),
        avg_minutes   = float(row["avg_minutes"]),
    )

# ==========================================
# STAGE 7: Centrality & Bottlenecks
# ==========================================
print("📊 Computing Centrality...")
in_degree    = dict(G.in_degree())
out_degree   = dict(G.out_degree())
weighted_in  = dict(G.in_degree(weight="trip_volume"))
weighted_out = dict(G.out_degree(weight="trip_volume"))

G_und = G.to_undirected()
betweenness_n = nx.betweenness_centrality(G_und, weight="weight", normalized=True)
closeness_n   = nx.closeness_centrality(G_und, distance="weight")
pagerank_n    = nx.pagerank(G, weight="trip_volume", alpha=0.85)
clustering_n  = nx.clustering(G_und, weight="weight")
edge_betw     = nx.edge_betweenness_centrality(G_und, weight="weight", normalized=True)

sla_breach_score = {
    n: sum(G[n][v]["pct_delayed"] * G[n][v]["trip_volume"] for v in G.successors(n))
    for n in G.nodes()
}
inbound_breach_score = {
    n: sum(G[u][n]["pct_delayed"] * G[u][n]["trip_volume"] for u in G.predecessors(n))
    for n in G.nodes()
}

node_df = pd.DataFrame({
    "hub_id"               : list(G.nodes()),
    "betweenness"          : [betweenness_n.get(n, 0)        for n in G.nodes()],
    "closeness"            : [closeness_n.get(n, 0)          for n in G.nodes()],
    "pagerank"             : [pagerank_n.get(n, 0)           for n in G.nodes()],
    "clustering"           : [clustering_n.get(n, 0)         for n in G.nodes()],
    "in_degree"            : [in_degree.get(n, 0)            for n in G.nodes()],
    "out_degree"           : [out_degree.get(n, 0)           for n in G.nodes()],
    "weighted_in"          : [weighted_in.get(n, 0)          for n in G.nodes()],
    "weighted_out"         : [weighted_out.get(n, 0)         for n in G.nodes()],
    "sla_breach_score"     : [sla_breach_score.get(n, 0)     for n in G.nodes()],
    "inbound_breach_score" : [inbound_breach_score.get(n, 0) for n in G.nodes()],
})

node_df["bottleneck_rank"] = (
    node_df["betweenness"].rank(pct=True) * 0.40 +
    node_df["sla_breach_score"].rank(pct=True) * 0.35 +
    node_df["pagerank"].rank(pct=True) * 0.15 +
    node_df["inbound_breach_score"].rank(pct=True) * 0.10
)
node_df = node_df.sort_values("bottleneck_rank", ascending=False).reset_index(drop=True)

edge_records = []
for (u, v), eb in edge_betw.items():
    if   G.has_edge(u, v): a, b = u, v
    elif G.has_edge(v, u): a, b = v, u
    else: continue
    edge_records.append({
        "src": a, "dst": b, "edge_betweenness": eb,
        "median_delay": G[a][b]["weight"],
        "pct_delayed":  G[a][b]["pct_delayed"],
        "trip_volume":  G[a][b]["trip_volume"],
    })
edge_df = pd.DataFrame(edge_records).sort_values("edge_betweenness", ascending=False)
chronic = edge_df[(edge_df["median_delay"] > 1.2) & (edge_df["trip_volume"] >= 5)].copy()
chronic = chronic.sort_values("pct_delayed", ascending=False).reset_index(drop=True)

node_df.to_csv(f"{ARTIFACTS_DIR}/node_df.csv", index=False)
edge_df.to_csv(f"{ARTIFACTS_DIR}/edge_df.csv", index=False)
node_df.head(50).to_csv(f"{ARTIFACTS_DIR}/bottleneck_hubs.csv", index=False)
chronic.to_csv(f"{ARTIFACTS_DIR}/chronic_corridors.csv", index=False)


# ==========================================
# STAGE 8a: Node2Vec Embeddings
# ==========================================
print("🧠 Training Node2Vec...")
EMBEDDING_DIM = 32
n2v = Node2Vec(G_und, dimensions=EMBEDDING_DIM, walk_length=30, num_walks=80, p=1.0, q=0.5, workers=1, quiet=True)
n2v_model = n2v.fit(window=5, min_count=1, batch_words=4)
n2v_emb = {n: (n2v_model.wv[n] if n in n2v_model.wv else np.zeros(EMBEDDING_DIM)) for n in G.nodes()}

n2v_df = pd.DataFrame.from_dict(n2v_emb, orient='index')
n2v_df.index.name = "hub_id"
n2v_df.to_csv(f"{ARTIFACTS_DIR}/node2vec_embeddings.csv")


# ==========================================
# STAGE 8b: GraphSAGE Embeddings (Unsupervised)
# ==========================================
print("🌐 Training Unsupervised GraphSAGE...")
CENTRALITY_LOOKUPS = {
    "betweenness"          : betweenness_n,
    "closeness"            : closeness_n,
    "pagerank"             : pagerank_n,
    "clustering"           : clustering_n,
    "in_degree"            : in_degree,
    "out_degree"           : out_degree,
    "weighted_in"          : weighted_in,
    "weighted_out"         : weighted_out,
    "sla_breach_score"     : sla_breach_score,
    "inbound_breach_score" : inbound_breach_score,
}
node_list  = list(G.nodes())
node_idx   = {n: i for i, n in enumerate(node_list)}
N_NODES    = len(node_list)
INPUT_DIM  = len(CENTRALITY_LOOKUPS)

X = np.zeros((N_NODES, INPUT_DIM), dtype=np.float32)
for j, (_, lookup) in enumerate(CENTRALITY_LOOKUPS.items()):
    X[:, j] = [lookup.get(n, 0.0) for n in node_list]
X = StandardScaler().fit_transform(X).astype(np.float32)

edge_pairs = [(node_idx[u], node_idx[v]) for u, v in G.edges()]
edge_index = torch.tensor(edge_pairs, dtype=torch.long).t().contiguous()
edge_weight = torch.tensor([G[u][v]["weight"] for u, v in G.edges()], dtype=torch.float)

data = Data(x=torch.tensor(X, dtype=torch.float), edge_index=edge_index, edge_weight=edge_weight)

class GraphSAGE(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, dropout=0.2):
        super().__init__()
        self.conv1   = SAGEConv(in_dim, hidden_dim, aggr="mean")
        self.conv2   = SAGEConv(hidden_dim, out_dim, aggr="mean")
        self.dropout = dropout
    def forward(self, x, edge_index):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=self.dropout, training=self.training)
        h = self.conv2(h, edge_index)
        return h

SAGE_OUT = 32
model_sage = GraphSAGE(INPUT_DIM, 64, SAGE_OUT)
optimizer  = torch.optim.Adam(model_sage.parameters(), lr=0.01)

model_sage.train()
n_edges_total = data.edge_index.size(1)
for epoch in range(150):
    optimizer.zero_grad()
    z = model_sage(data.x, data.edge_index)
    pos_idx = torch.randint(0, n_edges_total, (2048,))
    pos_src, pos_dst = data.edge_index[0, pos_idx], data.edge_index[1, pos_idx]
    neg_src = torch.randint(0, N_NODES, (2048,))
    neg_dst = torch.randint(0, N_NODES, (2048,))
    pos_logit = (z[pos_src] * z[pos_dst]).sum(dim=-1)
    neg_logit = (z[neg_src] * z[neg_dst]).sum(dim=-1)
    loss = -F.logsigmoid(pos_logit).mean() - F.logsigmoid(-neg_logit).mean()
    loss.backward()
    optimizer.step()

model_sage.eval()
with torch.no_grad():
    sage_matrix = model_sage(data.x, data.edge_index).numpy()
sage_emb = {node_list[i]: sage_matrix[i] for i in range(N_NODES)}

sage_df = pd.DataFrame.from_dict(sage_emb, orient='index')
sage_df.index.name = "hub_id"
sage_df.to_csv(f"{ARTIFACTS_DIR}/graphsage_embeddings.csv")


# ==========================================
# STAGE 8c: Supervised GraphSAGE (Delay-Prediction)
# ==========================================
print("📈 Training Supervised GraphSAGE...")
class SupervisedSAGE(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, dropout=0.3):
        super().__init__()
        self.conv1   = SAGEConv(in_dim,    hidden_dim, aggr="mean")
        self.conv2   = SAGEConv(hidden_dim, out_dim,   aggr="mean")
        self.pred    = nn.Linear(out_dim, 1)
        self.dropout = dropout
    def embed(self, x, edge_index):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=self.dropout, training=self.training)
        h = self.conv2(h, edge_index)
        return h
    def forward(self, x, edge_index):
        return self.pred(self.embed(x, edge_index)).squeeze()

node_target_map = df_train.groupby("source_center")["segment_actual_time"].mean().to_dict()
node_targets = torch.tensor([node_target_map.get(n, df_train["segment_actual_time"].median()) for n in node_list], dtype=torch.float)
y_mean = node_targets.mean()
y_std  = node_targets.std() + 1e-6
y_norm = (node_targets - y_mean) / y_std

data_sup = Data(x=torch.tensor(X, dtype=torch.float), edge_index=edge_index, y=y_norm)
sup_model = SupervisedSAGE(INPUT_DIM, 64, SAGE_OUT)
sup_optimizer = torch.optim.Adam(sup_model.parameters(), lr=0.005, weight_decay=1e-4)

sup_model.train()
for epoch in range(200):
    sup_optimizer.zero_grad()
    out = sup_model(data_sup.x, data_sup.edge_index)
    loss = F.mse_loss(out, data_sup.y)
    loss.backward()
    sup_optimizer.step()

sup_model.eval()
with torch.no_grad():
    sup_sage_matrix = sup_model.embed(data_sup.x, data_sup.edge_index).numpy()
sup_sage_emb = {node_list[i]: sup_sage_matrix[i] for i in range(N_NODES)}

sup_sage_df = pd.DataFrame.from_dict(sup_sage_emb, orient='index')
sup_sage_df.index.name = "hub_id"
sup_sage_df.to_csv(f"{ARTIFACTS_DIR}/sup_sage_embeddings.csv")


# ==========================================
# STAGE 9: XGBoost Models
# ==========================================
print("🎯 Training XGBoost ETA Models...")
def _stack_emb(series, lookup, dim):
    return np.stack(series.map(lambda x: lookup.get(x, np.zeros(dim))).values)

def _cosine_similarity_feature(df, emb_dict, dim, prefix):
    from sklearn.preprocessing import normalize as sk_normalize
    emb_matrix = np.array([emb_dict.get(n, np.zeros(dim)) for n in node_list])
    emb_normed = sk_normalize(emb_matrix)
    norm_lookup = {n: emb_normed[i] for i, n in enumerate(node_list)}
    zeros = np.zeros(dim)
    df[f"cos_sim_{prefix}"] = [
        float(np.dot(norm_lookup.get(s, zeros), norm_lookup.get(d, zeros)))
        for s, d in zip(df["source_center"], df["destination_center"])
    ]
    return df

def attach_graph_features(df):
    df = df.copy()
    for name, lookup in CENTRALITY_LOOKUPS.items():
        df[f"src_{name}"] = df["source_center"].map(lookup).fillna(0).astype(float)
        df[f"dst_{name}"] = df["destination_center"].map(lookup).fillna(0).astype(float)
    
    src_n2v = _stack_emb(df["source_center"], n2v_emb, EMBEDDING_DIM)
    dst_n2v = _stack_emb(df["destination_center"], n2v_emb, EMBEDDING_DIM)
    src_sage = _stack_emb(df["source_center"], sage_emb, SAGE_OUT)
    dst_sage = _stack_emb(df["destination_center"], sage_emb, SAGE_OUT)
    src_sup = _stack_emb(df["source_center"], sup_sage_emb, SAGE_OUT)
    dst_sup = _stack_emb(df["destination_center"], sup_sage_emb, SAGE_OUT)
    
    for i in range(EMBEDDING_DIM):
        df[f"src_n2v_{i}"] = src_n2v[:, i]
        df[f"dst_n2v_{i}"] = dst_n2v[:, i]
    for i in range(SAGE_OUT):
        df[f"src_sage_{i}"] = src_sage[:, i]
        df[f"dst_sage_{i}"] = dst_sage[:, i]
        df[f"src_sup_sage_{i}"] = src_sup[:, i]
        df[f"dst_sup_sage_{i}"] = dst_sup[:, i]
        
    df = _cosine_similarity_feature(df, n2v_emb, EMBEDDING_DIM, "n2v")
    df = _cosine_similarity_feature(df, sage_emb, SAGE_OUT, "sage")
    df = _cosine_similarity_feature(df, sup_sage_emb, SAGE_OUT, "sup_sage")
    
    return df

df_train_graph = attach_graph_features(df_train)
df_test_graph  = attach_graph_features(df_test)

BASE_FEATURES = [
    "segment_osrm_time", "segment_osrm_distance", "osrm_speed_kmh",
    "departure_hour", "hour_sin", "hour_cos", "is_weekend", "is_night_shipment",
    "route_type_encoded", "departure_day_of_week", "cutoff_factor", "is_cutoff",
    "corridor_median_delay", "corridor_mean_delay", "corridor_delay_std",
    "corridor_trip_volume",  "corridor_pct_delayed"
]
CENTRALITY_FEATURES = BASE_FEATURES + [f"src_{k}" for k in CENTRALITY_LOOKUPS] + [f"dst_{k}" for k in CENTRALITY_LOOKUPS]
N2V_FEATURES  = CENTRALITY_FEATURES + [f"src_n2v_{i}" for i in range(EMBEDDING_DIM)] + [f"dst_n2v_{i}" for i in range(EMBEDDING_DIM)] + ["cos_sim_n2v"]
SAGE_FEATURES = N2V_FEATURES + [f"src_sage_{i}" for i in range(SAGE_OUT)] + [f"dst_sage_{i}" for i in range(SAGE_OUT)] + ["cos_sim_sage"]
SUP_SAGE_FEATURES = SAGE_FEATURES + [f"src_sup_sage_{i}" for i in range(SAGE_OUT)] + [f"dst_sup_sage_{i}" for i in range(SAGE_OUT)] + ["cos_sim_sup_sage"]

TARGET = "segment_actual_time"
y_train, y_test = df_train_graph[TARGET].values, df_test_graph[TARGET].values

def within_pct(pred, actual, tol=0.15):
    return (np.abs(pred - actual) / np.clip(actual, 1e-6, None) <= tol).mean() * 100

results, models = {}, {}
specs = [
    ("Baseline", BASE_FEATURES),
    ("+ Centrality", CENTRALITY_FEATURES),
    ("+ Centrality + Node2Vec", N2V_FEATURES),
    ("+ Centrality + N2V + GraphSAGE(unsup)", SAGE_FEATURES),
    ("+ Cent + N2V + SAGE + SupervisedSAGE", SUP_SAGE_FEATURES)
]

for name, feats in specs:
    m = xgb.XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1)
    Xtr = df_train_graph[feats].fillna(0).values
    Xte = df_test_graph[feats].fillna(0).values
    m.fit(Xtr, y_train)
    pred = m.predict(Xte)
    mae  = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2   = r2_score(y_test, pred)
    w15  = within_pct(pred, y_test, 0.15)
    results[name] = {"Model": name, "MAE": mae, "RMSE": rmse, "R2": r2, "Within15": w15}
    models[name] = m

pd.DataFrame(list(results.values())).to_csv(f"{ARTIFACTS_DIR}/benchmark_results.csv", index=False)
joblib.dump(models["+ Cent + N2V + SAGE + SupervisedSAGE"], f"{ARTIFACTS_DIR}/best_xgb_model.pkl")

best = models["+ Cent + N2V + SAGE + SupervisedSAGE"]
fi = pd.DataFrame({"feature": SUP_SAGE_FEATURES, "importance": best.feature_importances_})
def categorise(f):
    if "_sup_sage_" in f: return "Supervised GraphSAGE (PRIMARY)"
    if "_sage_" in f: return "GraphSAGE embedding (unsup)"
    if "_n2v_"  in f: return "Node2Vec embedding"
    if any(k in f for k in ["betweenness","closeness","pagerank","clustering","degree","weighted","breach"]): return "Graph centrality"
    if f.startswith("corridor_"): return "Corridor aggregate"
    if f.startswith("cos_sim_"):  return "Cosine similarity"
    return "Trip / OSRM"
fi["category"] = fi["feature"].apply(categorise)
fi.to_csv(f"{ARTIFACTS_DIR}/feature_importance.csv", index=False)


# ==========================================
# Generate Metadata and Executive Metrics
# ==========================================
graph_metadata = {
    "nodes": G.number_of_nodes(),
    "edges": G.number_of_edges(),
    "segments_analysed": len(df),
    "embedding_dim": SAGE_OUT,
    "features": len(SUP_SAGE_FEATURES)
}
with open(f"{ARTIFACTS_DIR}/graph_metadata.json", "w") as f:
    json.dump(graph_metadata, f)

executive_metrics = {
    "total_facilities": G.number_of_nodes(),
    "total_corridors": G.number_of_edges(),
    "total_shipments": len(df),
    "sla_breach_rate": float(df_train["is_delayed"].mean() * 100),
    "baseline_mae": results["Baseline"]["MAE"],
    "final_mae": results["+ Cent + N2V + SAGE + SupervisedSAGE"]["MAE"],
    "graph_advantage_mae": results["Baseline"]["MAE"] - results["+ Cent + N2V + SAGE + SupervisedSAGE"]["MAE"],
    "within_15_improvement": results["+ Cent + N2V + SAGE + SupervisedSAGE"]["Within15"] - results["Baseline"]["Within15"]
}
with open(f"{ARTIFACTS_DIR}/executive_metrics.json", "w") as f:
    json.dump(executive_metrics, f)

print("✅ All artifacts successfully exported to /artifacts")
