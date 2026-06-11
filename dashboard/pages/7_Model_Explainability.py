import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css
from components.charts import plot_feature_importance

st.set_page_config(page_title="Model Explainability", page_icon="💡", layout="wide")
apply_custom_css()

st.title("Model Explainability")
st.markdown("What is the GraphSAGE-enhanced model actually looking at?")

fi_df = load_csv("feature_importance.csv")

if fi_df.empty:
    st.warning("Feature importance not found. Please run the artifact extraction script.")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    fig = plot_feature_importance(fi_df, top_n=20)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Importance by Category")
    cat_imp = fi_df.groupby("category")["importance"].sum().sort_values(ascending=False).reset_index()
    
    for _, row in cat_imp.iterrows():
        cat = row["category"]
        val = row["importance"] * 100
        
        # Color matching
        color = "blue"
        if "GraphSAGE" in cat: color = "amber"
        elif "centrality" in cat.lower(): color = "green"
        elif "Node2Vec" in cat: color = "blue"
        elif "OSRM" in cat: color = "red"
            
        st.markdown(f"""
        <div style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.05); border-left: 4px solid {'#f59e0b' if color=='amber' else '#3b82f6'}; border-radius: 4px;">
            <div style="font-size: 0.8rem; color: #94a3b8;">{cat}</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{val:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
st.markdown("---")
st.info("""
**Interpreter Note**: 
The OSRM features (distance, time) provide the base structure of the prediction, but the graph features fine-tune it. Notice how specific individual GraphSAGE latent dimensions show up in the top 20 — these dimensions have learned to encode the presence of downstream bottlenecks.
""")
