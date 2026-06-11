"""
Custom HTML metric cards for the Graph ML Platform dashboard.

Backwards compatible with existing pages:
    metric_card(label, value, delta=None, delta_type="neutral")
    badge(text, kind="blue")

Additions:
    metric_card(..., icon="🧠", unit="min", glow=True, sublabel="...", tooltip="...")
    prediction_tile(value, unit="mins", confidence=..., risk=..., features_used=...)
    leaderboard_row(rank, name, value, share_pct, color)
    contribution_card(category, importance_pct, kind="primary")
    pipeline_stage(icon, title, meta, kind="default")
"""

import streamlit as st


# Map legacy delta_type values to CSS classes.
_DELTA_CLASS = {
    "positive": "positive",
    "negative": "negative",
    "neutral":  "neutral",
    True:       "positive",
    False:      "negative",
    None:       "neutral",
}

_DELTA_ARROW = {
    "positive": "▲",
    "negative": "▼",
    "neutral":  "—",
}


def metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_type: str = "neutral",
    *,
    icon: str | None = None,
    unit: str | None = None,
    sublabel: str | None = None,
    glow: bool = False,
) -> None:
    """
    Render a premium glassmorphism metric card.

    Args mirror the legacy signature; keyword extras are optional.
    """
    cls = _DELTA_CLASS.get(delta_type, "neutral")
    arrow = _DELTA_ARROW.get(cls, "—")

    icon_html = ""
    if icon:
        icon_html = f'<span style="font-size:14px; opacity:0.9;">{icon}</span>'

    unit_html = f'<span class="gl-metric-unit">{unit}</span>' if unit else ""

    delta_html = ""
    if delta:
        delta_html = (
            f'<div class="gl-metric-delta {cls}">'
            f'<span>{arrow}</span><span>{delta}</span>'
            f'</div>'
        )

    sub_html = ""
    if sublabel:
        sub_html = (
            f'<div style="margin-top:6px; font-size:0.75rem; color:#64748B;'
            f'font-family:\'JetBrains Mono\',monospace;">{sublabel}</div>'
        )

    glow_cls = " gl-metric-glow" if glow else ""

    st.markdown(
        f"""
<div class="gl-metric{glow_cls}">
<div class="gl-metric-label">{icon_html}<span>{label}</span></div>
<div class="gl-metric-value">{value}{unit_html}</div>
{delta_html}
{sub_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "blue") -> None:
    """Render an inline status badge. kind: blue | purple | green | amber | red | gray."""
    st.markdown(f'<span class="gl-badge {kind}">{text}</span>', unsafe_allow_html=True)


def badge_html(text: str, kind: str = "blue") -> str:
    """Return the HTML string for a badge (use inside other HTML blocks)."""
    return f'<span class="gl-badge {kind}">{text}</span>'


def prediction_tile(
    value: str,
    unit: str = "mins",
    confidence: str | None = None,
    risk: str | None = None,
    features_used: int | None = None,
) -> None:
    """Mission-control prediction tile for the ETA Engine page."""
    parts = []
    if confidence is not None:
        parts.append(f"<span>CONFIDENCE: <strong style='color:#FFF'>{confidence}</strong></span>")
    if risk is not None:
        parts.append(f"<span>RISK: <strong style='color:#FFF'>{risk}</strong></span>")
    if features_used is not None:
        parts.append(f"<span>FEATURES: <strong style='color:#FFF'>{features_used}</strong></span>")
    sub_html = ""
    if parts:
        sub_html = '<div class="gl-prediction-sub">' + "".join(parts) + "</div>"

    st.markdown(
        f"""
<div class="gl-prediction">
<div class="gl-prediction-label">● PREDICTED ETA</div>
<div class="gl-prediction-value">{value}<span class="gl-prediction-unit"> {unit}</span></div>
{sub_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def contribution_card(category: str, importance_pct: float, kind: str = "blue") -> None:
    """Color-coded feature-importance category card (for Explainability page)."""
    color = {
        "blue":   ("#4F8CFF", "rgba(79,140,255,0.12)"),
        "purple": ("#7C3AED", "rgba(124,58,237,0.12)"),
        "green":  ("#10B981", "rgba(16,185,129,0.12)"),
        "amber":  ("#F59E0B", "rgba(245,158,11,0.12)"),
        "red":    ("#EF4444", "rgba(239,68,68,0.12)"),
    }.get(kind, ("#4F8CFF", "rgba(79,140,255,0.12)"))

    bar_w = max(0.0, min(100.0, importance_pct))

    st.markdown(
        f"""
<div style="
background: rgba(17,24,39,0.72);
border: 1px solid rgba(255,255,255,0.08);
border-left: 3px solid {color[0]};
border-radius: 12px; padding: 12px 14px;
margin-bottom: 10px;
transition: transform 160ms ease;">
<div style="display:flex; justify-content:space-between; align-items:baseline;">
<span style="font-size:0.78rem; color:#94A3B8; font-weight:600;
text-transform:uppercase; letter-spacing:0.08em;">{category}</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:1.05rem;
font-weight:700; color:#FFFFFF; font-variant-numeric:tabular-nums;">
{importance_pct:.1f}%
</span>
</div>
<div style="margin-top:8px; height:5px; border-radius:3px;
background: rgba(255,255,255,0.05); overflow:hidden;">
<div style="width:{bar_w}%; height:100%;
background: linear-gradient(90deg, {color[0]}, {color[0]}99);
box-shadow: 0 0 10px {color[1]};"></div>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def leaderboard_row(rank: int, name: str, value: str, share_pct: float | None = None,
                    color: str = "blue") -> None:
    """One row of a leaderboard (Model Benchmarks page)."""
    accent = {
        "blue":   "#4F8CFF",
        "purple": "#7C3AED",
        "green":  "#10B981",
        "amber":  "#F59E0B",
        "red":    "#EF4444",
    }.get(color, "#4F8CFF")
    share_html = ""
    if share_pct is not None:
        share_html = (
            f'<span style="font-family:\'JetBrains Mono\',monospace; font-size:0.8rem;'
            f'color:#94A3B8;">{share_pct:.1f}%</span>'
        )
    st.markdown(
        f"""
<div style="display:flex; align-items:center; justify-content:space-between;
padding: 12px 16px; margin-bottom: 8px;
background: rgba(17,24,39,0.72); border: 1px solid rgba(255,255,255,0.08);
border-radius: 12px;">
<div style="display:flex; align-items:center; gap:14px;">
<span style="width:28px; height:28px; border-radius:8px;
display:grid; place-items:center;
background: rgba(79,140,255,0.12); color:{accent};
font-family:'JetBrains Mono',monospace; font-weight:700;
font-size:0.85rem;">#{rank}</span>
<span style="color:#FFFFFF; font-weight:600;">{name}</span>
</div>
<div style="display:flex; align-items:center; gap:14px;">
{share_html}
<span style="font-family:'JetBrains Mono',monospace; font-weight:700;
color:#FFFFFF; font-variant-numeric:tabular-nums;">{value}</span>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def pipeline_stage(icon: str, title: str, meta: str = "", kind: str = "default") -> None:
    """Used by the Technical Architecture page."""
    cls = {"gnn": " gnn", "model": " model"}.get(kind, "")
    st.markdown(
        f"""
<div class="gl-stage{cls}">
<div class="gl-stage-icon">{icon}</div>
<div class="gl-stage-title">{title}</div>
<div class="gl-stage-meta">{meta}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def pipeline_arrow() -> None:
    st.markdown('<div class="gl-arrow">→</div>', unsafe_allow_html=True)
