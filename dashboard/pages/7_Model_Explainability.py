import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_csv
from components.aesthetics import apply_custom_css, hero, section, insight
from components.charts import plot_feature_importance
from components.metrics_cards import contribution_card, badge_html

st.set_page_config(page_title="Model Explainability · GraphML", page_icon="◆", layout="wide")
apply_custom_css()

fi_df = load_csv("feature_importance.csv")

if fi_df.empty:
    hero("STATUS", "Model Explainability", "Feature importance not found.",
         status="OFFLINE", status_kind="danger")
    st.warning("Please run the artifact extraction script.")
    st.stop()

hero(
    eyebrow="07 · INTERPRETABILITY",
    title="Model Explainability",
    subtitle="What the GraphSAGE-enhanced XGBoost is actually paying attention to — by feature, by category, by lineage.",
    status="MODEL · TRACED",
    meta=[f"Features · {len(fi_df):,}"],
)

insight(
    "OSRM features set the prediction's <strong>base</strong>; graph features <strong>fine-tune</strong> it. "
    "Specific GraphSAGE latent dimensions cracking the top-20 means those dimensions are encoding "
    "downstream bottleneck pressure — exactly the signal a non-graph baseline cannot see.",
    icon="◇",
)

col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(plot_feature_importance(fi_df, top_n=20), use_container_width=True)

with col2:
    section("Contribution by Category")

    cat_imp = (
        fi_df.groupby("category")["importance"].sum()
        .sort_values(ascending=False).reset_index()
    )
    total = max(cat_imp["importance"].sum(), 1e-9)

    for _, row in cat_imp.iterrows():
        cat = str(row["category"])
        pct = float(row["importance"]) / total * 100.0
        cn = cat.lower()
        if   "graphsage" in cn: kind = "purple"
        elif "node2vec"  in cn: kind = "blue"
        elif "central"   in cn: kind = "green"
        elif "osrm"      in cn: kind = "red"
        elif "temporal"  in cn or "time" in cn: kind = "amber"
        else: kind = "blue"
        contribution_card(cat, pct, kind=kind)

    st.markdown(
        f'<div style="margin-top:14px; display:flex; gap:6px; flex-wrap:wrap;">'
        f'{badge_html("GraphSAGE", "purple")} '
        f'{badge_html("Node2Vec", "blue")} '
        f'{badge_html("Centrality", "green")} '
        f'{badge_html("OSRM", "red")} '
        f'{badge_html("Temporal", "amber")}'
        f'</div>',
        unsafe_allow_html=True,
    )
