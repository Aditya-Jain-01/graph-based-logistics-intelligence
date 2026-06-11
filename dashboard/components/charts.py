"""
Plotly chart builders for the Graph ML Platform dashboard.

All charts use the shared dark glass theme defined in components.aesthetics.
Function signatures are preserved for backwards compatibility:
    plot_embeddings_tsne(emb_df, color_values, title="...")
    plot_waterfall_benchmark(benchmark_df)
    plot_feature_importance(fi_df, top_n=20)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:
    from sklearn.manifold import TSNE
    _HAS_TSNE = True
except Exception:  # pragma: no cover
    _HAS_TSNE = False

from .aesthetics import apply_plotly_theme, PALETTE


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
PRIMARY    = PALETTE["primary"]    # #4F8CFF
SECONDARY  = PALETTE["secondary"]  # #7C3AED
SUCCESS    = PALETTE["success"]    # #10B981
WARNING    = PALETTE["warning"]    # #F59E0B
DANGER     = PALETTE["danger"]     # #EF4444

# Continuous scale: cool -> warm (low risk -> high risk)
RISK_SCALE = [
    [0.00, "#1E3A8A"],
    [0.25, "#4F8CFF"],
    [0.50, "#7C3AED"],
    [0.75, "#F59E0B"],
    [1.00, "#EF4444"],
]

CATEGORY_COLORS = {
    "GraphSAGE":   SECONDARY,
    "Node2Vec":    PRIMARY,
    "OSRM":        DANGER,
    "Centrality":  SUCCESS,
    "Temporal":    WARNING,
    "Other":       "#64748B",
}


def _category_color(name: str) -> str:
    n = (name or "").lower()
    if "graphsage" in n: return SECONDARY
    if "node2vec"  in n: return PRIMARY
    if "osrm"      in n: return DANGER
    if "central"   in n: return SUCCESS
    if "temporal"  in n or "time" in n: return WARNING
    return "#64748B"


# ---------------------------------------------------------------------------
# t-SNE for embeddings
# ---------------------------------------------------------------------------
def plot_embeddings_tsne(emb_df: pd.DataFrame, color_values, title: str = "Embedding"):
    """2-D t-SNE projection of node embeddings, colored by bottleneck rank."""
    X = emb_df.values
    n = X.shape[0]

    if _HAS_TSNE and n >= 5:
        perplexity = max(5, min(30, n // 3))
        coords = TSNE(
            n_components=2, perplexity=perplexity, learning_rate="auto",
            init="pca", random_state=42,
        ).fit_transform(X)
    else:
        # Fallback: PCA via SVD
        Xc = X - X.mean(axis=0)
        u, s, vt = np.linalg.svd(Xc, full_matrices=False)
        coords = (u[:, :2] * s[:2])

    color_values = np.asarray(color_values, dtype=float)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=coords[:, 0], y=coords[:, 1],
            mode="markers",
            marker=dict(
                size=8,
                color=color_values,
                colorscale=RISK_SCALE,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Bottleneck<br>Rank", font=dict(color="#94A3B8", size=11)),
                    tickfont=dict(color="#94A3B8", size=10),
                    thickness=10, len=0.7, outlinewidth=0,
                ),
                line=dict(width=0.5, color="rgba(255,255,255,0.15)"),
                opacity=0.9,
            ),
            text=[f"hub: {h}" for h in emb_df.index],
            hovertemplate="<b>%{text}</b><br>risk=%{marker.color:.3f}<extra></extra>",
        )
    )

    apply_plotly_theme(fig, height=420)
    fig.update_layout(
        title=dict(text=title, x=0.0, xanchor="left"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# Benchmark waterfall (model ablation)
# ---------------------------------------------------------------------------
def plot_waterfall_benchmark(benchmark_df: pd.DataFrame):
    """Waterfall-style horizontal bar chart of MAE across model variants."""
    df = benchmark_df.copy()

    # Identify the metric column to plot (prefer MAE)
    metric_col = None
    for cand in ("mae", "MAE", "mean_absolute_error", "test_mae"):
        if cand in df.columns:
            metric_col = cand
            break
    if metric_col is None:
        # Take the first numeric column as fallback
        num_cols = df.select_dtypes(include=[np.number]).columns
        metric_col = num_cols[0] if len(num_cols) else df.columns[-1]

    name_col = None
    for cand in ("model", "Model", "name", "variant"):
        if cand in df.columns:
            name_col = cand
            break
    if name_col is None:
        name_col = df.columns[0]

    names = df[name_col].astype(str).tolist()
    values = df[metric_col].astype(float).tolist()

    # Color gradient: worst (highest MAE) red -> best (lowest) green
    vmax = max(values) if values else 1.0
    vmin = min(values) if values else 0.0
    rng = max(vmax - vmin, 1e-9)
    colors = []
    for v in values:
        # Lower MAE is better → bias toward primary/success
        t = (v - vmin) / rng
        if   t < 0.25: colors.append(SUCCESS)
        elif t < 0.55: colors.append(PRIMARY)
        elif t < 0.80: colors.append(SECONDARY)
        else:          colors.append(DANGER)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.08)", width=1),
            ),
            text=[f"{v:.2f}" for v in values],
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=12, family="JetBrains Mono"),
            hovertemplate="<b>%{y}</b><br>MAE: %{x:.3f} min<extra></extra>",
        )
    )

    apply_plotly_theme(fig, hovermode="y unified", height=380)
    fig.update_layout(
        title=dict(text="Progressive Ablation — MAE (lower is better)", x=0.0, xanchor="left"),
        xaxis=dict(title=metric_col.upper(), gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(title="", autorange="reversed", showgrid=False),
        margin=dict(l=20, r=60, t=50, b=40),
        showlegend=False,
        bargap=0.35,
    )
    return fig


# ---------------------------------------------------------------------------
# Feature importance (categorical)
# ---------------------------------------------------------------------------
def plot_feature_importance(fi_df: pd.DataFrame, top_n: int = 20):
    """Top-N feature importance, colored by category."""
    df = fi_df.copy()

    feat_col = next((c for c in ("feature", "name", "Feature") if c in df.columns), df.columns[0])
    imp_col  = next((c for c in ("importance", "Importance", "value") if c in df.columns), df.columns[1])
    cat_col  = next((c for c in ("category", "Category", "group") if c in df.columns), None)

    df = df.sort_values(imp_col, ascending=False).head(top_n).iloc[::-1]
    feats = df[feat_col].astype(str).tolist()
    imps  = df[imp_col].astype(float).tolist()
    cats  = (df[cat_col].astype(str).tolist() if cat_col else ["Other"] * len(feats))
    colors = [_category_color(c) for c in cats]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=imps,
            y=feats,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.08)", width=1),
            ),
            customdata=cats,
            hovertemplate="<b>%{y}</b><br>category: %{customdata}<br>importance: %{x:.4f}<extra></extra>",
        )
    )

    apply_plotly_theme(fig, hovermode="y unified", height=560)
    fig.update_layout(
        title=dict(text=f"Top {top_n} Feature Importances", x=0.0, xanchor="left"),
        xaxis=dict(title="Importance", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(title="", showgrid=False, tickfont=dict(size=11, color="#C9D2E1")),
        margin=dict(l=20, r=20, t=50, b=40),
        showlegend=False,
        bargap=0.25,
    )

    # Add a soft category legend via shapes-free annotation strip
    seen = []
    for c in cats:
        if c not in seen: seen.append(c)
    legend_text = "  ".join(
        f"<span style='color:{_category_color(c)}'>■</span> "
        f"<span style='color:#94A3B8'>{c}</span>"
        for c in seen
    )
    fig.add_annotation(
        text=legend_text,
        xref="paper", yref="paper", x=0.0, y=1.08,
        showarrow=False, align="left",
        font=dict(family="Inter", size=11, color="#94A3B8"),
    )
    return fig
