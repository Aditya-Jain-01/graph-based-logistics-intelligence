import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_json
from components.aesthetics import apply_custom_css

st.set_page_config(page_title="Technical Architecture", page_icon="🏗️", layout="wide")
apply_custom_css()

st.title("Technical Architecture")
st.markdown("End-to-End ML Pipeline & Data Flow")

meta = load_json("graph_metadata.json")
if not meta:
    st.warning("Metadata not found. Please run the artifact extraction script.")
    st.stop()

st.markdown("""
```mermaid
graph TD
    A[Raw Delivery Data<br>144k rows] --> B(Feature Engineering<br>& Aggregation)
    B --> C[Corridor Statistics<br>Median Delay, Vol]
    B --> D[OD Level Stats]
    
    C --> E((Directed Weighted Graph<br>NetworkX))
    D --> E
    
    E --> F[Graph Centrality<br>Stage 7]
    E --> G[Node2Vec Random Walks<br>Stage 8a]
    E --> H[GraphSAGE Message Passing<br>PyTorch Geo - Stage 8b]
    
    F --> I{Feature Vectorization}
    G --> I
    H --> I
    C --> I
    
    I --> J(XGBoost Regressor<br>Stage 9)
    J --> K[Predicted ETA &<br>Feature Importance]
    
    style E fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style H fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style J fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc
```
""")

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 📊 Graph Specification")
    st.write(f"- **Nodes (Hubs)**: {meta.get('nodes', 0):,}")
    st.write(f"- **Edges (Corridors)**: {meta.get('edges', 0):,}")
    st.write(f"- **Total Training Segments**: {meta.get('segments_analysed', 0):,}")

with col2:
    st.markdown("### 🧠 GNN Specification")
    st.write("- **Architecture**: GraphSAGE")
    st.write("- **Framework**: PyTorch Geometric")
    st.write("- **Layers**: 2 (2-hop neighborhood)")
    st.write("- **Hidden Dim**: 64")
    st.write(f"- **Output Embedding Dim**: {meta.get('embedding_dim', 32)}")
    st.write("- **Objective**: Supervised Delay Prediction (MSE)")

with col3:
    st.markdown("### 🚀 ETA Model Specification")
    st.write("- **Model**: XGBoost Regressor")
    st.write("- **Objective**: Squared Error")
    st.write(f"- **Total Features**: {meta.get('features', 0)}")
    st.write("- **Hyperparameters**: lr=0.05, depth=6, n_estimators=400")

st.markdown("---")
st.info("💡 **Design Decision**: Why separate the pipeline? Graph traversal and GNN message passing are expensive operations. By exporting the models and embeddings offline (`export_artifacts.py`), this dashboard serves inferences and visualisations instantly without recalculating network structures on the fly.")
