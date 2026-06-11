import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv, load_json
from components.aesthetics import apply_custom_css, hero, section, insight
from components.charts import plot_embeddings_tsne
from components.metrics_cards import badge_html

st.set_page_config(page_title="Graph Embeddings Lab · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

node2vec_df  = load_csv("node2vec_embeddings.csv")
graphsage_df = load_csv("graphsage_embeddings.csv")
sup_sage_df  = load_csv("sup_sage_embeddings.csv")
node_df      = load_csv("node_df.csv")

if node2vec_df.empty or graphsage_df.empty or sup_sage_df.empty:
    hero("STATUS", "Graph Embeddings Lab", "Embeddings not found.", status="OFFLINE", status_kind="danger")
    st.warning("Please run the artifact extraction script.")
    st.stop()

if "hub_id" in node2vec_df.columns:  node2vec_df.set_index("hub_id", inplace=True)
if "hub_id" in graphsage_df.columns: graphsage_df.set_index("hub_id", inplace=True)
if "hub_id" in sup_sage_df.columns:  sup_sage_df.set_index("hub_id", inplace=True)

ranks = []
for hub in node2vec_df.index:
    rank_val = node_df[node_df["hub_id"] == hub]["bottleneck_rank"].values
    ranks.append(rank_val[0] if len(rank_val) > 0 else 0)

hero(
    eyebrow="04 · REPRESENTATION LEARNING",
    title="Graph Embeddings Lab",
    subtitle="The visual story behind our node representations — a research-paper view of how three models learn the network's risk surface.",
    status="EMBEDDINGS · 3 LOADED",
    meta=["dim=32", f"hubs={len(node2vec_df):,}"],
)

insight(
    "Each panel projects 32-D embeddings into 2-D via t-SNE, "
    "coloured by composite <strong>bottleneck rank</strong>. The story is the progressive separation "
    "of high-risk hubs (red) from healthy ones (blue) as the model gains supervision.",
    icon="◎",
)

STEPS = [
    {
        "num": "STEP 01",
        "title": "Node2Vec",
        "badges": [("Random walks", "blue"), ("Unsupervised", "gray")],
        "body": "32-D vectors learned from biased random walks on the graph. "
                "Captures topology but ignores hub features and delay signals.",
        "df": node2vec_df,
        "plot_title": "Node2Vec",
        "verdict": ("Mixed risk across clusters · weak separation", "amber"),
    },
    {
        "num": "STEP 02",
        "title": "GraphSAGE · Unsupervised",
        "badges": [("Message passing", "purple"), ("Unsupervised", "gray")],
        "body": "Aggregates each hub's own features with its neighbours' features over 2 hops. "
                "Combines structure and content — but still without delay labels.",
        "df": graphsage_df,
        "plot_title": "GraphSAGE (Unsup)",
        "verdict": ("Tighter clusters, partial risk separation", "blue"),
    },
    {
        "num": "STEP 03 · PRIMARY",
        "title": "Supervised GraphSAGE",
        "badges": [("Message passing", "purple"), ("Supervised on delay", "green")],
        "body": "Same message-passing backbone, but explicitly trained to predict node-level delay. "
                "This is the embedding we feed into the production XGBoost ETA model.",
        "df": sup_sage_df,
        "plot_title": "Supervised SAGE",
        "verdict": ("Sharp cluster of high-risk hubs", "green"),
    },
]

for step in STEPS:
    section(step["num"] + " · " + step["title"])
    col_text, col_plot = st.columns([1, 1.7])
    with col_text:
        badges_html = " ".join(badge_html(t, k) for t, k in step["badges"])
        verdict_text, verdict_kind = step["verdict"]
        st.markdown(
            f'<div class="gl-step">'
            f'<div class="gl-step-num">{step["num"]}</div>'
            f'<h3>{step["title"]}</h3>'
            f'<div style="margin-bottom:10px;">{badges_html}</div>'
            f'<p>{step["body"]}</p>'
            f'<div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06);">'
            f'<div style="font-size:0.7rem; color:#64748B; letter-spacing:0.14em; font-weight:700; text-transform:uppercase; margin-bottom:6px;">Verdict</div>'
            f'{badge_html(verdict_text, verdict_kind)}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with col_plot:
        fig = plot_embeddings_tsne(step["df"], ranks, title=step["plot_title"])
        st.plotly_chart(fig, use_container_width=True)

insight(
    "<strong>Why this matters:</strong> the Supervised GraphSAGE projection cleanly isolates the chronically "
    "delayed regions of the network. That separation is exactly what gives the downstream XGBoost regressor its "
    "predictive lift — see the <em>Model Benchmarks</em> page for the quantified gain.",
    icon="▲",
)
