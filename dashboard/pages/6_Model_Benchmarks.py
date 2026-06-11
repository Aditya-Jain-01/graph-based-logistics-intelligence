import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css, hero, section, insight
from components.charts import plot_waterfall_benchmark
from components.metrics_cards import leaderboard_row, badge_html

st.set_page_config(page_title="Model Benchmarks · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

benchmarks = load_csv("benchmark_results.csv")

if benchmarks.empty:
    hero("STATUS", "Model Benchmarks", "Benchmark results not found.",
         status="OFFLINE", status_kind="danger")
    st.warning("Please run the artifact extraction script.")
    st.stop()

hero(
    eyebrow="06 · ABLATION",
    title="Model Benchmarks",
    subtitle="Five XGBoost variants, identical hyperparameters, different feature sets. The delta tells us exactly what graph learning is worth.",
    status="BENCHMARK · LOCKED",
    meta=[f"Variants · {len(benchmarks)}"],
)

insight(
    "Each row swaps in a richer feature layer. The gap between the baseline and the GraphSAGE-augmented "
    "model is the <strong>Graph Advantage</strong> — and it maps directly to SLA penalty avoided.",
    icon="∑",
)

# ----- Leaderboard -----
section("Leaderboard · Mean Absolute Error")
metric_col = next((c for c in ("mae", "MAE", "mean_absolute_error", "test_mae") if c in benchmarks.columns), None)
name_col   = next((c for c in ("model", "Model", "name", "variant") if c in benchmarks.columns), benchmarks.columns[0])

if metric_col:
    ranked = benchmarks.sort_values(metric_col, ascending=True).reset_index(drop=True)
    best = ranked[metric_col].iloc[0]
    worst = ranked[metric_col].iloc[-1]
    for i, row in ranked.iterrows():
        v = float(row[metric_col])
        delta = (worst - v) / max(worst - best, 1e-9) * 100  # % of full improvement captured
        color = "green" if i == 0 else ("blue" if i < 3 else "amber" if i < 4 else "red")
        leaderboard_row(i + 1, str(row[name_col]),
                        value=f"{v:.3f} min",
                        share_pct=delta if i > 0 else None,
                        color=color)
else:
    st.dataframe(benchmarks, use_container_width=True, hide_index=True)

# ----- Visual + Narrative -----
section("Progressive Ablation")
c1, c2 = st.columns([2, 1])
with c1:
    st.plotly_chart(plot_waterfall_benchmark(benchmarks), use_container_width=True)
with c2:
    st.markdown(
        f'<div class="gl-card" style="height:100%;">'
        f'<div class="gl-card-title">Verdict</div>'
        f'<h3 style="margin:4px 0 10px;">Graph learning is doing the work</h3>'
        f'<div style="margin-bottom:12px;">{badge_html("Primary signal", "green")} '
        f'{badge_html("GraphSAGE", "purple")}</div>'
        '<p style="color:#C9D2E1; font-size:0.92rem; line-height:1.65;">'
        'The baseline captures distance and time but misses network constraints. '
        '<strong>Centrality</strong> adds structural risk. <strong>Node2Vec</strong> adds topological context. '
        '<strong>GraphSAGE</strong> gives the model recursive awareness of a hub\'s 2-hop operational health — '
        'the single largest contributor to the within-15% accuracy lift.'
        '</p></div>',
        unsafe_allow_html=True,
    )

section("Raw Results")
st.dataframe(benchmarks, use_container_width=True, hide_index=True)
