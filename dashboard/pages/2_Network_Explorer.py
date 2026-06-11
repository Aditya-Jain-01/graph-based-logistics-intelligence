import streamlit as st
import sys
import os
import networkx as nx
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_graph, load_csv
from components.aesthetics import apply_custom_css

st.set_page_config(page_title="Network Explorer", page_icon="🌐", layout="wide")
apply_custom_css()

st.title("Network Explorer")
st.markdown("Interactive visualization of hub dependencies and structural relationships.")

G = load_graph()
node_df = load_csv("node_df.csv")

if G.number_of_nodes() == 0:
    st.warning("Graph data not found. Please run `python export_artifacts.py`.")
    st.stop()

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Search Hub")
    all_hubs = sorted(list(G.nodes()))
    selected_hub = st.selectbox("Select Hub ID", all_hubs, index=0 if len(all_hubs) > 0 else None)
    
    if selected_hub:
        st.markdown("#### Structural Profile")
        hub_data = node_df[node_df["hub_id"] == selected_hub]
        if not hub_data.empty:
            st.metric("Composite Bottleneck Rank", f"{hub_data['bottleneck_rank'].values[0]:.3f}")
            st.metric("Betweenness Centrality", f"{hub_data['betweenness'].values[0]:.4f}")
            st.metric("PageRank", f"{hub_data['pagerank'].values[0]:.4f}")
            st.metric("In Degree", f"{hub_data['in_degree'].values[0]:.0f}")
            st.metric("Out Degree", f"{hub_data['out_degree'].values[0]:.0f}")

with col2:
    if selected_hub:
        st.markdown(f"### Ego-Network for `{selected_hub}`")
        st.caption("Showing immediate predecessors and successors (1-hop neighbourhood).")
        
        # Build ego network
        in_nodes = list(G.predecessors(selected_hub))
        out_nodes = list(G.successors(selected_hub))
        ego_nodes = set([selected_hub] + in_nodes + out_nodes)
        
        H = G.subgraph(ego_nodes)
        
        # Layout
        pos = nx.spring_layout(H, seed=42)
        
        edge_x, edge_y = [], []
        for u, v in H.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y, line=dict(width=1.5, color='#475569'),
            hoverinfo='none', mode='lines'
        )
        
        node_x = [pos[node][0] for node in H.nodes()]
        node_y = [pos[node][1] for node in H.nodes()]
        
        node_colors = []
        for n in H.nodes():
            if n == selected_hub: node_colors.append('#ef4444')
            elif n in in_nodes: node_colors.append('#3b82f6')
            else: node_colors.append('#10b981')
            
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            hoverinfo='text',
            marker=dict(size=20, color=node_colors, lineWidth=2, line_color='white'),
            text=[n[-6:] for n in H.nodes()],
            textposition="top center",
            hovertext=list(H.nodes())
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0,l=0,r=0,t=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
             )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Legend:** 
        🔴 Selected Hub | 🔵 Inbound Neighbors | 🟢 Outbound Neighbors
        """)
