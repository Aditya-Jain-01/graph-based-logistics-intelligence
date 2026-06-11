import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_waterfall_benchmark(benchmark_df):
    """
    Renders a waterfall chart for Graph Advantage decomposition.
    """
    if benchmark_df.empty:
        return go.Figure()
        
    benchmark_df = pd.DataFrame(benchmark_df)
    models = benchmark_df["Model"].tolist()
    maes = benchmark_df["MAE"].tolist()
    
    # Calculate differences
    diffs = [maes[0]]
    for i in range(1, len(maes)):
        diffs.append(maes[i] - maes[i-1])
        
    measure = ["absolute"] + ["relative"] * (len(maes) - 1)
    
    fig = go.Figure(go.Waterfall(
        name="MAE (minutes)",
        orientation="v",
        measure=measure,
        x=[m.replace("+ ", "") for m in models],
        textposition="outside",
        text=[f"{v:.2f}" for v in diffs],
        y=diffs,
        connector={"line":{"color":"#475569"}},
        decreasing={"marker":{"color":"#10b981"}},
        increasing={"marker":{"color":"#ef4444"}},
        totals={"marker":{"color":"#3b82f6"}}
    ))
    
    fig.update_layout(
        title="MAE Reduction (Graph Advantage)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        yaxis_title="Mean Absolute Error (minutes)",
        waterfallgap=0.3,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    return fig

def plot_feature_importance(fi_df, top_n=15):
    """
    Renders feature importance bar chart colored by category.
    """
    if fi_df.empty:
        return go.Figure()
        
    fi_df = fi_df.sort_values("importance", ascending=True).tail(top_n)
    
    color_map = {
        "GraphSAGE embedding (PRIMARY)": "#a855f7",
        "Node2Vec embedding": "#3b82f6",
        "Graph centrality": "#10b981",
        "Corridor aggregate": "#f59e0b",
        "Trip / OSRM": "#64748b"
    }
    
    fig = px.bar(
        fi_df, x="importance", y="feature", color="category",
        orientation='h', color_discrete_map=color_map,
        title=f"Top {top_n} Features Driving ETA Prediction"
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        xaxis_title="Importance Score",
        yaxis_title="",
        legend_title="Feature Category",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def plot_embeddings_tsne(emb_df, ranks, title="t-SNE Embeddings"):
    """
    Renders an interactive 2D scatter of embeddings.
    """
    if emb_df.empty or len(ranks) != len(emb_df):
        return go.Figure()
        
    # Standard fallback if not 2D
    from sklearn.manifold import TSNE
    if emb_df.shape[1] > 2:
        tsne = TSNE(n_components=2, random_state=42, init="pca", learning_rate="auto")
        proj = tsne.fit_transform(emb_df.values)
    else:
        proj = emb_df.values
        
    df_plot = pd.DataFrame({
        "x": proj[:, 0],
        "y": proj[:, 1],
        "hub_id": emb_df.index,
        "bottleneck_rank": ranks
    })
    
    fig = px.scatter(
        df_plot, x="x", y="y", color="bottleneck_rank", hover_name="hub_id",
        color_continuous_scale="Plasma",
        title=title
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        coloraxis_colorbar=dict(title="Bottleneck Rank")
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color='white')))
    
    return fig
