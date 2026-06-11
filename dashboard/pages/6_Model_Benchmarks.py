import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css
from components.charts import plot_waterfall_benchmark

st.set_page_config(page_title="Model Benchmarks", page_icon="📈", layout="wide")
apply_custom_css()

st.title("Model Benchmarks")
st.markdown("Ablation study decomposing the *Graph Advantage* into measurable components.")

benchmarks = load_csv("benchmark_results.csv")

if benchmarks.empty:
    st.warning("Benchmark results not found. Please run the artifact extraction script.")
    st.stop()

st.markdown("""
### The Five-Model Progressive Benchmark
We trained five XGBoost regressors with identical hyperparameters. Only the feature sets change, allowing us to explicitly measure the value of Graph Representation Learning over standard OSRM heuristics.
""")

st.dataframe(benchmarks, use_container_width=True, hide_index=True)

st.markdown("---")

c1, c2 = st.columns([2, 1])

with c1:
    fig = plot_waterfall_benchmark(benchmarks)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### 🏆 Conclusion")
    st.info("""
    **Key Takeaway**:
    The baseline model captures general distance and time, but fundamentally misunderstands the network constraints. 
    
    By adding **Graph Centrality**, we teach the model about structural risk. 
    By adding **Node2Vec**, we teach it about topological neighborhoods. 
    But by adding **GraphSAGE**, we give the model recursive awareness of the operational health (delay risk) of a hub's 2-hop neighborhood.
    
    The resulting jump in *Within-15% Accuracy* translates directly into massive SLA penalty savings.
    """)
