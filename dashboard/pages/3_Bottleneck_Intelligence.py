import streamlit as st
import sys
import os
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css

st.set_page_config(page_title="Bottleneck Intelligence", page_icon="🏭", layout="wide")
apply_custom_css()

st.title("Bottleneck Intelligence")
st.markdown("Identify the structural constraints driving network SLA breaches.")

node_df = load_csv("node_df.csv")
chronic_corridors = load_csv("chronic_corridors.csv")

if node_df.empty:
    st.warning("Data not found. Please run the artifact extraction script.")
    st.stop()

st.markdown("### Structural Risk vs. Operational Pain")
st.markdown("Hubs in the top-right quadrant are critical chokepoints: they sit on many shortest paths (High Betweenness) AND actively cause delays (High SLA Breach Score).")

# Scatter Plot
fig = px.scatter(
    node_df, x="betweenness", y="sla_breach_score", 
    color="pagerank", size="out_degree",
    hover_name="hub_id",
    color_continuous_scale="Viridis",
    labels={"betweenness": "Betweenness Centrality (Structural Risk)", 
            "sla_breach_score": "SLA Breach Score (Operational Pain)"}
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cbd5e1")
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚠️ Top 10 Chronic Corridors")
    st.dataframe(chronic_corridors.head(10)[['src', 'dst', 'median_delay', 'pct_delayed', 'trip_volume']], use_container_width=True)
    
with col2:
    st.markdown("### 🛠️ Recommended Interventions")
    st.info("""
    **Intervention Framework:**
    - **High Median Delay + High FTL Confidence:** Route-type shift from Carting to FTL.
    - **High Edge Betweenness + Delay > 1.2x:** Parallel route activation required.
    - **High Delay Std (Variance):** Facility process audit.
    - **Downstream of Top Bottleneck:** Address upstream dependency first.
    """)
