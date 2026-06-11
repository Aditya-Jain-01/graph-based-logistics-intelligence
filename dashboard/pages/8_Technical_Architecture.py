import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_json
from components.aesthetics import apply_custom_css, hero, section, insight
from components.metrics_cards import pipeline_stage, pipeline_arrow, badge_html, metric_card

st.set_page_config(page_title="Technical Architecture · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

meta = load_json("graph_metadata.json")
if not meta:
    hero("STATUS", "Technical Architecture", "Metadata not found.",
         status="OFFLINE", status_kind="danger")
    st.warning("Please run the artifact extraction script.")
    st.stop()

hero(
    eyebrow="08 · PLATFORM",
    title="Technical Architecture",
    subtitle="The end-to-end ML pipeline behind the dashboard — from raw delivery rows to live ETA inference.",
    status="PIPELINE · GREEN",
    meta=[f"Features · {meta.get('features', 0)}", f"Emb dim · {meta.get('embedding_dim', 32)}"],
)

# -------- Stylized pipeline (6 stages with arrows) --------
section("Inference Pipeline")
stages = [
    ("⛁", "Raw Delivery Data",     "~144k rows",           "default"),
    ("⚙", "Feature Engineering",   "aggregation",          "default"),
    ("◆", "Graph Construction",    f"{meta.get('nodes', 0):,} nodes",     "default"),
    ("∿", "Centrality + Node2Vec", "structural features",  "default"),
    ("✦", "GraphSAGE (PyG)",       f"dim={meta.get('embedding_dim', 32)}",          "gnn"),
    ("▶", "XGBoost Regressor",     f"{meta.get('features', 0)} features", "model"),
]

# Render 6 stages with 5 arrows between them => 11 columns
cols = st.columns([1, 0.18] * 5 + [1])
for i, (icon, title, mta, kind) in enumerate(stages):
    with cols[i * 2]:
        pipeline_stage(icon, title, mta, kind=kind)
    if i < len(stages) - 1:
        with cols[i * 2 + 1]:
            pipeline_arrow()

insight(
    "We separate <strong>offline training</strong> from <strong>online inference</strong>. "
    "Graph traversal, message passing and embedding generation happen in <code>export_artifacts.py</code>. "
    "The dashboard only consumes cached embeddings, the serialized graph and the XGBoost booster — "
    "keeping p50 inference under 50 ms.",
    icon="◇",
)

# -------- Specs --------
section("System Specifications")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="gl-card"><div class="gl-card-title">Graph</div>'
        f'<h3 style="margin:4px 0 10px;">Directed · Weighted</h3>'
        f'<div style="margin-bottom:12px;">{badge_html("NetworkX", "blue")}</div>'
        f'<p style="color:#C9D2E1; font-size:0.9rem; line-height:1.7; margin:0;">'
        f'<strong style="color:#FFF">Nodes (Hubs):</strong> {meta.get("nodes", 0):,}<br>'
        f'<strong style="color:#FFF">Edges (Corridors):</strong> {meta.get("edges", 0):,}<br>'
        f'<strong style="color:#FFF">Segments:</strong> {meta.get("segments_analysed", 0):,}'
        f'</p></div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f'<div class="gl-card"><div class="gl-card-title">GNN</div>'
        f'<h3 style="margin:4px 0 10px;">GraphSAGE · 2 layers</h3>'
        f'<div style="margin-bottom:12px;">{badge_html("PyTorch Geometric", "purple")} '
        f'{badge_html("Supervised", "green")}</div>'
        f'<p style="color:#C9D2E1; font-size:0.9rem; line-height:1.7; margin:0;">'
        f'<strong style="color:#FFF">Hidden dim:</strong> 64<br>'
        f'<strong style="color:#FFF">Output dim:</strong> {meta.get("embedding_dim", 32)}<br>'
        f'<strong style="color:#FFF">Objective:</strong> MSE on node delay<br>'
        f'<strong style="color:#FFF">Neighbourhood:</strong> 2-hop'
        f'</p></div>',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f'<div class="gl-card"><div class="gl-card-title">ETA Model</div>'
        f'<h3 style="margin:4px 0 10px;">XGBoost Regressor</h3>'
        f'<div style="margin-bottom:12px;">{badge_html("squared error", "amber")} '
        f'{badge_html("400 trees", "blue")}</div>'
        f'<p style="color:#C9D2E1; font-size:0.9rem; line-height:1.7; margin:0;">'
        f'<strong style="color:#FFF">Features:</strong> {meta.get("features", 0)}<br>'
        f'<strong style="color:#FFF">Learning rate:</strong> 0.05<br>'
        f'<strong style="color:#FFF">Max depth:</strong> 6<br>'
        f'<strong style="color:#FFF">Estimators:</strong> 400'
        f'</p></div>',
        unsafe_allow_html=True,
    )

# -------- Runtime KPIs --------
section("Runtime Profile")
r1, r2, r3, r4 = st.columns(4)
with r1: metric_card("Cold-start", "< 2.0", unit="s", icon="⟳", delta="artifacts cached", delta_type="positive")
with r2: metric_card("Inference p50", "< 50", unit="ms", icon="●", delta="warm path", delta_type="positive")
with r3: metric_card("Embedding Refresh", "nightly", icon="◇", sublabel="export_artifacts.py")
with r4: metric_card("Graph Footprint", f"{meta.get('nodes', 0):,}",
                     icon="◆", sublabel="nodes in memory")
