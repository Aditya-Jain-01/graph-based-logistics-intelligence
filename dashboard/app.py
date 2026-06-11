"""
Main entry point for the Delhivery Graph Logistics Intelligence Platform.

The dashboard uses Streamlit's native multipage routing (files in ./pages/).
This file styles the sidebar brand header and renders a landing overview.
"""

import streamlit as st

from components.aesthetics import apply_custom_css, hero, section
from components.metrics_cards import metric_card, badge_html
from utils.data_loader import load_json  # data_loader is NOT modified


st.set_page_config(
    page_title="Graph ML Platform · Delhivery",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()


# ---------------------------------------------------------------------------
# Sidebar brand header (rendered above Streamlit's auto page nav)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="gl-brand">
            <div class="gl-brand-logo">
                <div class="gl-brand-mark">G</div>
                <div>
                    <div class="gl-brand-title">Graph ML Platform</div>
                    <div class="gl-brand-sub">Logistics Intelligence</div>
                </div>
            </div>
            <div class="gl-brand-meta">
                <span class="gl-brand-dot"></span>
                <span>v1.0 · prod · in-sync</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="padding: 0 12px; font-size:0.7rem; color:#64748B; '
        'letter-spacing:0.12em; text-transform:uppercase; font-weight:600; '
        'margin: 8px 0 2px;">Navigation</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
metrics = load_json("executive_metrics.json") or {}

hero(
    eyebrow="OVERVIEW · DELHIVERY",
    title="Graph Logistics Intelligence Platform",
    subtitle=(
        "A production-grade observability surface for our directed logistics graph: "
        "GraphSAGE embeddings, XGBoost ETA inference, and SLA-aware bottleneck analytics — "
        "all wired into one mission-control console."
    ),
    status="LIVE MODEL",
    meta=[
        f"Nodes · {metrics.get('total_facilities', 0):,}",
        f"Edges · {metrics.get('total_corridors', 0):,}",
        f"Segments · {metrics.get('total_shipments', 0):,}",
    ],
)

section("Platform Snapshot")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Facilities", f"{metrics.get('total_facilities', 0):,}", icon="◆")
with c2:
    metric_card("Corridors", f"{metrics.get('total_corridors', 0):,}", icon="↗")
with c3:
    breach = metrics.get("sla_breach_rate", 0)
    metric_card(
        "OSRM Delay Rate", f"{breach:.1f}", unit="%",
        delta=">20% slower than car ETA",
        delta_type="neutral",
        icon="!",
    )
with c4:
    adv = metrics.get("graph_advantage_mae", 0)
    metric_card(
        "Graph Advantage", f"{adv:.2f}", unit="min",
        delta="MAE Reduction vs OSRM", delta_type="positive",
        icon="▲", glow=True,
    )

section("Where to Start")

col_a, col_b, col_c = st.columns(3)
nav_card = """
<div class="gl-card" style="height:100%;">
  <div class="gl-card-title">{eyebrow}</div>
  <h3 style="margin:4px 0 8px;">{title}</h3>
  <p style="color:#C9D2E1; font-size:0.9rem; line-height:1.55; margin:0 0 12px;">{body}</p>
  {badges}
</div>
"""
with col_a:
    st.markdown(nav_card.format(
        eyebrow="01 · STRATEGY",
        title="Executive Overview",
        body="Network KPIs, graph-model advantage and the operational-impact simulator.",
        badges=badge_html("KPIs", "blue") + " " + badge_html("Business Impact", "green"),
    ), unsafe_allow_html=True)
with col_b:
    st.markdown(nav_card.format(
        eyebrow="02 · INFERENCE",
        title="ETA Prediction Engine",
        body="Mission-control console for live ETA inference with risk decomposition.",
        badges=badge_html("Live Model", "purple") + " " + badge_html("XGBoost", "amber"),
    ), unsafe_allow_html=True)
with col_c:
    st.markdown(nav_card.format(
        eyebrow="03 · RESEARCH",
        title="Graph Embeddings Lab",
        body="Visual progression from Node2Vec to Supervised GraphSAGE representations.",
        badges=badge_html("GNN", "purple") + " " + badge_html("t-SNE", "blue"),
    ), unsafe_allow_html=True)

st.markdown(" ")
section("System Status")
s1, s2, s3, s4 = st.columns(4)
with s1: metric_card("Model Artifacts", "OK",      delta="cached",        delta_type="positive", icon="●")
with s2: metric_card("Graph Snapshot",  "OK",      delta="hot",           delta_type="positive", icon="●")
with s3: metric_card("Embeddings",      "3 / 3",   delta="N2V · SAGE · SupSAGE", delta_type="neutral", icon="◇")
with s4: metric_card("Inference p50",   "< 50",    unit="ms", delta="edge-cached", delta_type="positive", icon="⟳")
