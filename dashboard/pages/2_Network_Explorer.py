import streamlit as st
import sys
import os
import networkx as nx
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_graph, load_csv
from components.aesthetics import apply_custom_css, hero, section, insight, apply_plotly_theme
from components.metrics_cards import metric_card, badge_html

st.set_page_config(page_title="Network Explorer · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

G = load_graph()
node_df = load_csv("node_df.csv")

if G.number_of_nodes() == 0:
    hero("STATUS", "Network Explorer", "Graph data not found.", status="OFFLINE", status_kind="danger")
    st.warning("Please run `python export_artifacts.py`.")
    st.stop()

hero(
    eyebrow="02 · TOPOLOGY",
    title="Network Explorer",
    subtitle="A cyber-ops view of the directed logistics graph — pick any hub to inspect its risk score, centrality and 1-hop blast radius.",
    status="GRAPH SYNCED",
    meta=[f"|V| · {G.number_of_nodes():,}", f"|E| · {G.number_of_edges():,}"],
)

# Layout: Left = Hub Intelligence | Right = Graph
left, right = st.columns([1, 2.2])

all_hubs = sorted(list(G.nodes()))

with left:
    st.markdown(
        '<div class="gl-card"><div class="gl-card-title">Hub Intelligence</div>',
        unsafe_allow_html=True,
    )
    selected_hub = st.selectbox("Select Hub ID", all_hubs, index=0, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_hub:
        hub_data = node_df[node_df["hub_id"] == selected_hub] if not node_df.empty else None
        if hub_data is not None and not hub_data.empty:
            br  = float(hub_data["bottleneck_rank"].values[0])
            bw  = float(hub_data["betweenness"].values[0])
            pr  = float(hub_data["pagerank"].values[0])
            indg  = int(hub_data["in_degree"].values[0])
            outdg = int(hub_data["out_degree"].values[0])

            risk_kind = "danger" if br > 0.7 else ("amber" if br > 0.4 else "green")
            risk_label = "HIGH RISK" if br > 0.7 else ("MEDIUM" if br > 0.4 else "LOW RISK")

            st.markdown(
                f'<div style="margin-top:12px;">{badge_html(risk_label, risk_kind)} '
                f'{badge_html(f"deg={indg+outdg}", "blue")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(" ")
            metric_card("Bottleneck Rank", f"{br:.3f}", icon="!",
                        delta_type="negative" if br > 0.5 else "positive",
                        delta=f"percentile of risk",
                        glow=br > 0.7)
            metric_card("Betweenness", f"{bw:.4f}", icon="◇", sublabel="structural risk")
            metric_card("PageRank", f"{pr:.4f}", icon="◆", sublabel="influence")
            cA, cB = st.columns(2)
            with cA: metric_card("In-Degree", f"{indg}", icon="←")
            with cB: metric_card("Out-Degree", f"{outdg}", icon="→")

with right:
    if selected_hub:
        in_nodes  = list(G.predecessors(selected_hub))
        out_nodes = list(G.successors(selected_hub))
        ego_nodes = set([selected_hub] + in_nodes + out_nodes)
        H = G.subgraph(ego_nodes)

        section(f"Ego-Network · {selected_hub}")
        insight(
            f"Showing the 1-hop neighbourhood — <strong>{len(in_nodes)} upstream</strong> "
            f"feeders and <strong>{len(out_nodes)} downstream</strong> dependants. "
            "Red = selected hub, blue = predecessor, purple = successor.",
            icon="◎",
        )

        pos = nx.spring_layout(H, seed=42, k=0.8)

        edge_x, edge_y = [], []
        for u, v in H.edges():
            x0, y0 = pos[u]; x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.0, color="rgba(148,163,184,0.35)"),
            hoverinfo="none", mode="lines",
        )

        node_x, node_y, node_colors, node_sizes, node_text, node_line = [], [], [], [], [], []
        for n in H.nodes():
            x, y = pos[n]
            node_x.append(x); node_y.append(y)
            if n == selected_hub:
                node_colors.append("#EF4444"); node_sizes.append(34)
                node_line.append("#FCA5A5")
            elif n in in_nodes:
                node_colors.append("#4F8CFF"); node_sizes.append(18)
                node_line.append("rgba(255,255,255,0.18)")
            else:
                node_colors.append("#7C3AED"); node_sizes.append(18)
                node_line.append("rgba(255,255,255,0.18)")
            node_text.append(f"<b>{n}</b>")

        node_trace = go.Scatter(
            x=node_x, y=node_y, mode="markers",
            marker=dict(
                size=node_sizes, color=node_colors,
                line=dict(color=node_line, width=1.5),
                opacity=0.95,
            ),
            text=node_text, hoverinfo="text",
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        apply_plotly_theme(fig, height=560)
        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
