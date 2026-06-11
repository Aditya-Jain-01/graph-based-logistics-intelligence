import streamlit as st
import sys
import os
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css, hero, section, insight, apply_plotly_theme
from components.metrics_cards import metric_card, badge_html

st.set_page_config(page_title="Bottleneck Intelligence · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

node_df = load_csv("node_df.csv")
chronic_corridors = load_csv("chronic_corridors.csv")

if node_df.empty:
    hero("STATUS", "Bottleneck Intelligence", "Data not found.", status="OFFLINE", status_kind="danger")
    st.warning("Please run the artifact extraction script.")
    st.stop()

hero(
    eyebrow="03 · DIAGNOSTICS",
    title="Bottleneck Intelligence",
    subtitle="Where structural risk meets operational pain. Surfaces the hubs and corridors driving the breach rate.",
    status="MODEL · OK",
    meta=[f"Hubs · {len(node_df):,}", f"Chronic Corridors · {len(chronic_corridors):,}"],
)

section("Risk Quadrant")
insight(
    "Top-right = <strong>critical chokepoint</strong>: high betweenness <em>and</em> high SLA breach. "
    "These hubs sit on many shortest paths <em>and</em> actively cause delay — prioritise CapEx here.",
    icon="⌖",
)

fig = px.scatter(
    node_df, x="betweenness", y="sla_breach_score",
    color="pagerank", size="out_degree",
    hover_name="hub_id",
    color_continuous_scale=[[0, "#4F8CFF"], [0.5, "#7C3AED"], [1, "#EF4444"]],
    labels={
        "betweenness": "Betweenness · Structural Risk",
        "sla_breach_score": "SLA Breach Score · Operational Pain",
        "pagerank": "PageRank",
    },
)
apply_plotly_theme(fig, height=460)
fig.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.18)", width=0.6), opacity=0.85))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns([1.4, 1])

with col1:
    section("Top 10 Chronic Corridors")
    cols = [c for c in ["src", "dst", "median_delay", "pct_delayed", "trip_volume"] if c in chronic_corridors.columns]
    st.dataframe(chronic_corridors.head(10)[cols], use_container_width=True, hide_index=True)

with col2:
    section("Intervention Playbook")
    st.markdown(
        f'<div class="gl-card">'
        f'<div style="margin-bottom:10px;">{badge_html("Framework", "blue")}</div>'
        '<p style="color:#C9D2E1; font-size:0.92rem; line-height:1.7; margin:0;">'
        '<strong style="color:#FFF">High Median Delay + FTL viable</strong> · Route-type shift Carting → FTL.<br>'
        '<strong style="color:#FFF">High Edge Betweenness + Delay × 1.2</strong> · Activate parallel route.<br>'
        '<strong style="color:#FFF">High Delay Variance</strong> · Facility process audit.<br>'
        '<strong style="color:#FFF">Downstream of top bottleneck</strong> · Fix upstream first.'
        '</p></div>',
        unsafe_allow_html=True,
    )
