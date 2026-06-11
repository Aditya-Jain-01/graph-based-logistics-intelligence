import os
import json
import joblib
import pandas as pd
import streamlit as st
import networkx as nx

ARTIFACTS_DIR = "artifacts"

@st.cache_data(show_spinner=False)
def load_csv(filename):
    filepath = os.path.join(ARTIFACTS_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_json(filename):
    filepath = os.path.join(ARTIFACTS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

@st.cache_resource(show_spinner=False)
def load_xgb_model(filename="best_xgb_model.pkl"):
    filepath = os.path.join(ARTIFACTS_DIR, filename)
    if os.path.exists(filepath):
        return joblib.load(filepath)
    return None

@st.cache_data(show_spinner=False)
def load_graph():
    node_df = load_csv("node_df.csv")
    edge_df = load_csv("edge_df.csv")
    
    if node_df.empty or edge_df.empty:
        return nx.DiGraph()
        
    G = nx.DiGraph()
    for _, row in node_df.iterrows():
        G.add_node(row["hub_id"], **row.to_dict())
    
    for _, row in edge_df.iterrows():
        G.add_edge(row["src"], row["dst"], **row.to_dict())
        
    return G

@st.cache_data(show_spinner=False)
def load_all_artifacts():
    return {
        "node_df": load_csv("node_df.csv"),
        "edge_df": load_csv("edge_df.csv"),
        "bottleneck_hubs": load_csv("bottleneck_hubs.csv"),
        "chronic_corridors": load_csv("chronic_corridors.csv"),
        "node2vec_embeddings": load_csv("node2vec_embeddings.csv"),
        "graphsage_embeddings": load_csv("graphsage_embeddings.csv"),
        "sup_sage_embeddings": load_csv("sup_sage_embeddings.csv"),
        "feature_importance": load_csv("feature_importance.csv"),
        "benchmark_results": load_csv("benchmark_results.csv"),
        "graph_metadata": load_json("graph_metadata.json"),
        "executive_metrics": load_json("executive_metrics.json"),
    }
