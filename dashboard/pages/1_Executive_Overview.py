import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_json, load_csv
from components.aesthetics import apply_custom_css
from components.metrics_cards import metric_card, badge

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
apply_custom_css()

st.title("Executive Overview")
st.markdown("### High-Level Network State & Business Impact")

# Load artifacts
metrics = load_json("executive_metrics.json")
bottleneck_hubs = load_csv("bottleneck_hubs.csv")
chronic_corridors = load_csv("chronic_corridors.csv")

if not metrics:
    st.warning("Metrics artifact not found. Please run `python export_artifacts.py` to generate the offline models and metrics.")
    st.stop()

# 1. KPIs Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Facilities (Nodes)", f"{metrics.get('total_facilities', 0):,}")
with c2:
    metric_card("Active Corridors (Edges)", f"{metrics.get('total_corridors', 0):,}")
with c3:
    metric_card("Segments Analysed", f"{metrics.get('total_shipments', 0):,}")
with c4:
    breach = metrics.get('sla_breach_rate', 0)
    metric_card("SLA Breach Rate", f"{breach:.1f}%", delta="Target < 20%", delta_type="negative" if breach > 20 else "positive")

st.markdown("---")

# 2. Graph Advantage & Business Impact
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 ETA Prediction Advantage")
    st.markdown("Comparing the GraphSAGE-enhanced XGBoost model against the OSRM baseline.")
    
    b_mae = metrics.get('baseline_mae', 0)
    f_mae = metrics.get('final_mae', 0)
    adv_mae = metrics.get('graph_advantage_mae', 0)
    w15 = metrics.get('within_15_improvement', 0)
    
    mc1, mc2 = st.columns(2)
    with mc1:
        metric_card("Baseline MAE", f"{b_mae:.2f} min")
        metric_card("GraphSAGE MAE", f"{f_mae:.2f} min", delta=f"-{adv_mae:.2f} min", delta_type="positive")
    with mc2:
        metric_card("Within-15% Accuracy Lift", f"+{w15:.2f} pp", delta="Critical SLA Metric", delta_type="positive")

with col2:
    st.markdown("### 💼 Operations Strategy Simulation")
    st.info("**Scenario**: What would happen if the top 3 bottleneck hubs were upgraded to reduce their delays by 25%?")
    
    if not bottleneck_hubs.empty:
        top3_score = bottleneck_hubs.head(3)['sla_breach_score'].sum()
        total_score = bottleneck_hubs['sla_breach_score'].sum()
        top3_share = top3_score / max(total_score, 1e-6)
        
        projected_sla_reduction = top3_share * 0.25
        revenue_recovered = projected_sla_reduction * (breach / 100) * 6000 # Approximation based on 60Cr per pp
        
        sc1, sc2 = st.columns(2)
        with sc1:
            metric_card("Projected SLA Reduction", f"-{(projected_sla_reduction*100):.1f} pp", delta_type="positive")
        with sc2:
            metric_card("Revenue-at-Risk Recovered", f"INR ~{revenue_recovered:.1f} Cr", delta="Annualised", delta_type="positive")
            
st.markdown("---")

# 3. Top Bottlenecks
st.markdown("### 🏭 Top 5 Bottleneck Hubs")
if not bottleneck_hubs.empty:
    st.dataframe(bottleneck_hubs.head(5)[["hub_id", "bottleneck_rank", "betweenness", "sla_breach_score", "pagerank"]], use_container_width=True)
else:
    st.caption("Bottleneck data unavailable.")
