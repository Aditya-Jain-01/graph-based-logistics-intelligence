import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_json, load_csv
from components.aesthetics import apply_custom_css, hero, section, insight, apply_plotly_theme
from components.metrics_cards import metric_card, badge_html

st.set_page_config(page_title="Executive Overview · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

metrics = load_json("executive_metrics.json")
bottleneck_hubs = load_csv("bottleneck_hubs.csv")
chronic_corridors = load_csv("chronic_corridors.csv")

if not metrics:
    hero("STATUS", "Executive Overview", "Metrics artifact not found.", status="OFFLINE", status_kind="danger")
    st.warning("Please run `python export_artifacts.py` to generate the offline models and metrics.")
    st.stop()

breach = metrics.get("sla_breach_rate", 0)

hero(
    eyebrow="01 · STRATEGY",
    title="Executive Overview",
    subtitle="A unified read on network health, model advantage and the business case for graph-enhanced ETA prediction.",
    status="LIVE MODEL",
    meta=[
        f"Updated · today",
        f"OSRM Delay · {breach:.1f}%",
        f"Δ MAE · {metrics.get('graph_advantage_mae', 0):.2f}m reduction",
    ],
)

# -------- Row 1: Executive KPIs --------
section("Network Snapshot")
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Facilities", f"{metrics.get('total_facilities', 0):,}", icon="◆",
                sublabel="graph nodes")
with c2:
    metric_card("Active Corridors", f"{metrics.get('total_corridors', 0):,}", icon="↗",
                sublabel="directed edges")
with c3:
    metric_card("Segments Analysed", f"{metrics.get('total_shipments', 0):,}", icon="∑",
                sublabel="training rows")
with c4:
    metric_card(
        "OSRM Delay Rate", f"{breach:.1f}", unit="%",
        delta=">20% slower than car ETA",
        delta_type="neutral",
        icon="!",
        glow=False,
    )

# -------- Row 2: Impact analysis cards --------
section("Graph Advantage · Business Impact")
insight(
    "GraphSAGE-enhanced XGBoost cuts mean ETA error by "
    f"<strong>{metrics.get('graph_advantage_mae', 0):.2f} minutes</strong> versus the OSRM baseline, "
    f"lifting within-15% accuracy by <strong>+{metrics.get('within_15_improvement', 0):.2f} pp</strong> — "
    "the threshold that gates our SLA-penalty exposure.",
    icon="▲",
)

b_mae = metrics.get("baseline_mae", 0)
f_mae = metrics.get("final_mae", 0)
adv   = metrics.get("graph_advantage_mae", 0)
w15   = metrics.get("within_15_improvement", 0)

k1, k2, k3, k4 = st.columns(4)
with k1: metric_card("Baseline MAE", f"{b_mae:.2f}", unit="min", icon="○", sublabel="OSRM only")
with k2: metric_card("GraphSAGE MAE", f"{f_mae:.2f}", unit="min",
                     delta=f"{adv:.2f} min reduction", delta_type="positive", icon="●", glow=True,
                     sublabel="primary model")
with k3: metric_card("Within-15% Lift", f"+{w15:.2f}", unit="pp",
                     delta="Critical SLA gate", delta_type="positive", icon="▲")
with k4:
    # Heuristic revenue card – purely visual; uses same metric scale already exposed.
    saved = (adv / max(b_mae, 1e-6)) * 100.0
    metric_card("Error Reduction", f"{saved:.1f}", unit="%",
                delta="vs baseline", delta_type="positive", icon="%")

# -------- Row 3: Bottlenecks + Strategy panel --------
section("Top Bottlenecks · Strategy Simulator")
left, right = st.columns([1.45, 1])

with left:
    st.markdown(
        '<div class="gl-card">'
        '<div class="gl-card-title">Top 10 Bottleneck Hubs · SLA Breach Score</div>',
        unsafe_allow_html=True,
    )
    if not bottleneck_hubs.empty:
        top = bottleneck_hubs.head(10).copy()
        if "sla_breach_score" in top.columns and "hub_id" in top.columns:
            fig = go.Figure(go.Bar(
                x=top["sla_breach_score"][::-1],
                y=top["hub_id"][::-1],
                orientation="h",
                marker=dict(
                    color=top["sla_breach_score"][::-1],
                    colorscale=[[0, "#4F8CFF"], [0.5, "#7C3AED"], [1, "#EF4444"]],
                    line=dict(color="rgba(255,255,255,0.08)", width=1),
                ),
                hovertemplate="<b>%{y}</b><br>SLA breach score: %{x:.2f}<extra></extra>",
            ))
            apply_plotly_theme(fig, height=380)
            fig.update_layout(
                xaxis=dict(title="SLA Breach Score"),
                yaxis=dict(title=""),
                margin=dict(l=10, r=10, t=10, b=30),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(top, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(
        '<div class="gl-card" style="height:100%;">'
        '<div class="gl-card-title">Operations Strategy Simulator</div>'
        '<h3 style="margin:0 0 10px;">Upgrade the top 3 bottlenecks</h3>'
        '<p style="color:#C9D2E1; font-size:0.92rem; line-height:1.55;">'
        'If the top three bottleneck hubs were upgraded to cut their delay '
        'contribution by 25%, what would land on the SLA line?</p>',
        unsafe_allow_html=True,
    )
    if not bottleneck_hubs.empty and "sla_breach_score" in bottleneck_hubs.columns:
        top3_score = bottleneck_hubs.head(3)["sla_breach_score"].sum()
        total_score = bottleneck_hubs["sla_breach_score"].sum()
        top3_share = top3_score / max(total_score, 1e-6)
        projected = top3_share * 0.25
        st.markdown(" ")
        metric_card("Projected SLA Improvement",
                    f"{projected*100:.2f}", unit="pp",
                    delta=f"top-3 share · {top3_share*100:.1f}%",
                    delta_type="positive", icon="▲", glow=True)
        st.markdown(
            f'<div style="margin-top:14px;">{badge_html("CapEx priority", "amber")} '
            f'{badge_html("Quick win", "green")} {badge_html("Quarter 1", "blue")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Chronic corridors strip --------
section("Chronic Corridors")
if not chronic_corridors.empty:
    cols = [c for c in ["src", "dst", "median_delay", "pct_delayed", "trip_volume"] if c in chronic_corridors.columns]
    st.dataframe(chronic_corridors.head(8)[cols], use_container_width=True, hide_index=True)
