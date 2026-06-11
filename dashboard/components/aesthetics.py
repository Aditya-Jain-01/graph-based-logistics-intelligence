"""
Global CSS injection for the Delhivery Graph Logistics Intelligence Platform.

Design system:
  - Base:        #070B14
  - Surface:     rgba(17,24,39,0.72)  (glassmorphism + backdrop-blur)
  - Border:      rgba(255,255,255,0.08)
  - Primary:     #4F8CFF
  - Secondary:   #7C3AED
  - Success:     #10B981
  - Warning:     #F59E0B
  - Danger:      #EF4444
  - Font:        Inter (already loaded)
"""

import streamlit as st


PALETTE = {
    "base":      "#070B14",
    "surface":   "rgba(17,24,39,0.72)",
    "surface_2": "rgba(23,32,49,0.65)",
    "border":    "rgba(255,255,255,0.08)",
    "border_2":  "rgba(255,255,255,0.14)",
    "text":      "#E5E7EB",
    "muted":     "#94A3B8",
    "subtle":    "#64748B",
    "primary":   "#4F8CFF",
    "secondary": "#7C3AED",
    "success":   "#10B981",
    "warning":   "#F59E0B",
    "danger":    "#EF4444",
}


def apply_custom_css() -> None:
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

        <style>
        :root {
            --gl-base: #070B14;
            --gl-surface: rgba(17,24,39,0.72);
            --gl-surface-2: rgba(23,32,49,0.65);
            --gl-border: rgba(255,255,255,0.08);
            --gl-border-2: rgba(255,255,255,0.14);
            --gl-text: #E5E7EB;
            --gl-muted: #94A3B8;
            --gl-subtle: #64748B;
            --gl-primary: #4F8CFF;
            --gl-secondary: #7C3AED;
            --gl-success: #10B981;
            --gl-warning: #F59E0B;
            --gl-danger: #EF4444;
            --gl-glow-primary: 0 0 40px rgba(79,140,255,0.18);
            --gl-glow-success: 0 0 40px rgba(16,185,129,0.18);
            --gl-shadow-card: 0 1px 0 rgba(255,255,255,0.04) inset,
                              0 12px 32px -12px rgba(0,0,0,0.6),
                              0 2px 4px -1px rgba(0,0,0,0.4);
        }

        /* ----- Global reset ----- */
        html, body, [class*="css"], .stApp, .main {
            background: var(--gl-base) !important;
            color: var(--gl-text) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-feature-settings: 'cv11', 'ss01', 'ss03';
            -webkit-font-smoothing: antialiased;
        }

        .stApp {
            background:
              radial-gradient(1200px 600px at 15% -10%, rgba(79,140,255,0.10), transparent 60%),
              radial-gradient(900px 500px at 110% 10%, rgba(124,58,237,0.10), transparent 55%),
              var(--gl-base) !important;
        }

        /* Streamlit's top toolbar - hide chrome */
        header[data-testid="stHeader"] {
            background: transparent !important;
            backdrop-filter: blur(6px);
        }
        #MainMenu, footer { visibility: hidden; }

        /* Main container padding */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1480px;
        }

        /* ----- Typography ----- */
        h1, h2, h3, h4, h5 {
            color: var(--gl-text) !important;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em !important;
            font-weight: 700 !important;
        }
        h1 {
            font-size: 2.5rem !important;
            line-height: 1.1 !important;
            background: linear-gradient(135deg, #FFFFFF 0%, #B6C7E6 60%, #4F8CFF 120%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.25rem !important;
        }
        h2 { font-size: 1.5rem !important; letter-spacing: -0.015em !important; }
        h3 { font-size: 1.125rem !important; font-weight: 600 !important; }
        h4 { font-size: 0.95rem !important; font-weight: 600 !important; color: var(--gl-muted) !important; text-transform: uppercase; letter-spacing: 0.08em !important; }

        p, span, div, label { color: var(--gl-text); }
        .stMarkdown p { color: #C9D2E1; line-height: 1.6; }

        /* ----- Sidebar ----- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0A1020 0%, #070B14 100%) !important;
            border-right: 1px solid var(--gl-border);
            box-shadow: inset -1px 0 0 rgba(255,255,255,0.03);
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0.5rem;
        }
        section[data-testid="stSidebar"] .stMarkdown { color: var(--gl-muted); }
        section[data-testid="stSidebar"] a {
            display: flex; align-items: center; gap: 0.6rem;
            padding: 0.55rem 0.85rem !important;
            margin: 2px 6px !important;
            border-radius: 8px !important;
            color: #B6C2D6 !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            transition: all 160ms ease;
            border: 1px solid transparent;
        }
        section[data-testid="stSidebar"] a:hover {
            background: rgba(79,140,255,0.08) !important;
            color: #FFFFFF !important;
            border-color: var(--gl-border);
        }
        /* Active nav indicator */
        section[data-testid="stSidebar"] a[aria-current="page"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: linear-gradient(90deg, rgba(79,140,255,0.18), rgba(124,58,237,0.08)) !important;
            color: #FFFFFF !important;
            border-color: rgba(79,140,255,0.35) !important;
            box-shadow: inset 2px 0 0 var(--gl-primary);
        }

        /* Brand header (rendered as markdown block in app.py) */
        .gl-brand {
            padding: 1rem 1rem 0.85rem;
            margin: 0 0 0.5rem;
            border-bottom: 1px solid var(--gl-border);
        }
        .gl-brand-logo {
            display: flex; align-items: center; gap: 10px;
        }
        .gl-brand-mark {
            width: 30px; height: 30px; border-radius: 8px;
            background: linear-gradient(135deg, #4F8CFF, #7C3AED);
            box-shadow: 0 0 18px rgba(79,140,255,0.45);
            display: grid; place-items: center;
            color: white; font-weight: 800; font-size: 14px;
            font-family: 'JetBrains Mono', monospace;
        }
        .gl-brand-title {
            font-size: 0.7rem; font-weight: 700; letter-spacing: 0.18em;
            color: var(--gl-muted); text-transform: uppercase;
        }
        .gl-brand-sub {
            font-size: 0.95rem; font-weight: 600; color: #FFFFFF;
            letter-spacing: -0.01em; margin-top: 2px;
        }
        .gl-brand-meta {
            display: flex; align-items: center; gap: 6px;
            font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
            color: var(--gl-subtle); margin-top: 10px;
        }
        .gl-brand-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: var(--gl-success);
            box-shadow: 0 0 8px var(--gl-success);
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%,100% { opacity: 1; transform: scale(1); }
            50%     { opacity: 0.55; transform: scale(0.92); }
        }

        /* ----- Hero block ----- */
        .gl-hero {
            display: flex; align-items: flex-start; justify-content: space-between;
            gap: 24px; padding: 8px 0 22px;
            border-bottom: 1px solid var(--gl-border);
            margin-bottom: 28px;
        }
        .gl-hero-left { max-width: 820px; }
        .gl-hero-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem; letter-spacing: 0.22em;
            color: var(--gl-primary); text-transform: uppercase;
            margin-bottom: 10px; font-weight: 600;
        }
        .gl-hero-title {
            font-size: 2.4rem; font-weight: 700; line-height: 1.05;
            letter-spacing: -0.025em; margin: 0;
            background: linear-gradient(135deg, #FFFFFF 0%, #B6C7E6 70%, #4F8CFF 130%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .gl-hero-sub {
            margin-top: 10px; color: var(--gl-muted);
            font-size: 1rem; max-width: 760px; line-height: 1.55;
        }
        .gl-hero-right {
            display: flex; flex-direction: column; align-items: flex-end; gap: 8px;
        }
        .gl-status {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 6px 12px; border-radius: 999px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
            color: var(--gl-success);
            background: rgba(16,185,129,0.08);
            border: 1px solid rgba(16,185,129,0.28);
        }
        .gl-status::before {
            content: ''; width: 7px; height: 7px; border-radius: 50%;
            background: var(--gl-success); box-shadow: 0 0 10px var(--gl-success);
            animation: pulse 1.8s ease-in-out infinite;
        }
        .gl-meta-chip {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem; color: var(--gl-subtle);
            padding: 4px 10px; border-radius: 6px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--gl-border);
        }

        /* ----- Cards (insight, narrative, generic) ----- */
        .gl-card {
            background: var(--gl-surface);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--gl-border);
            border-radius: 14px;
            padding: 22px 22px;
            box-shadow: var(--gl-shadow-card);
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }
        .gl-card:hover {
            transform: translateY(-2px);
            border-color: var(--gl-border-2);
        }
        .gl-card-title {
            font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em;
            color: var(--gl-muted); text-transform: uppercase;
            margin-bottom: 10px;
        }

        .gl-insight {
            display: flex; gap: 14px; align-items: flex-start;
            background: linear-gradient(135deg, rgba(79,140,255,0.08), rgba(124,58,237,0.04));
            border: 1px solid rgba(79,140,255,0.22);
            border-radius: 12px; padding: 14px 16px;
            margin: 6px 0 18px;
        }
        .gl-insight-icon {
            width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0;
            background: linear-gradient(135deg, #4F8CFF, #7C3AED);
            display: grid; place-items: center; color: white;
            font-weight: 700; font-size: 14px;
            box-shadow: 0 0 14px rgba(79,140,255,0.4);
        }
        .gl-insight-body { font-size: 0.92rem; color: #D7DEEC; line-height: 1.55; }
        .gl-insight-body strong { color: #FFFFFF; }

        /* ----- Section header ----- */
        .gl-section {
            display: flex; align-items: center; justify-content: space-between;
            margin: 28px 0 14px;
        }
        .gl-section h3 {
            margin: 0; font-size: 1rem !important;
            font-weight: 600 !important; color: #FFFFFF !important;
            letter-spacing: -0.01em !important;
        }
        .gl-section-rule {
            flex: 1; height: 1px; margin-left: 14px;
            background: linear-gradient(90deg, var(--gl-border), transparent);
        }

        /* ----- Metric cards (HTML in metrics_cards.py) ----- */
        .gl-metric {
            position: relative; overflow: hidden;
            background: var(--gl-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--gl-border);
            border-radius: 14px;
            padding: 18px 20px 16px;
            box-shadow: var(--gl-shadow-card);
            transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
        }
        .gl-metric::before {
            content: ''; position: absolute; inset: 0;
            background: radial-gradient(400px 120px at 0% 0%, rgba(79,140,255,0.08), transparent 60%);
            pointer-events: none;
        }
        .gl-metric:hover {
            transform: translateY(-4px);
            border-color: rgba(79,140,255,0.32);
            box-shadow: var(--gl-shadow-card), var(--gl-glow-primary);
        }
        .gl-metric-label {
            display: flex; align-items: center; gap: 8px;
            font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em;
            color: var(--gl-muted); text-transform: uppercase;
        }
        .gl-metric-value {
            font-size: 2rem; font-weight: 700; line-height: 1.1;
            margin-top: 8px; color: #FFFFFF;
            letter-spacing: -0.02em;
            font-variant-numeric: tabular-nums;
        }
        .gl-metric-unit {
            font-size: 0.9rem; font-weight: 500; color: var(--gl-muted);
            margin-left: 4px;
        }
        .gl-metric-delta {
            display: inline-flex; align-items: center; gap: 4px;
            margin-top: 10px; font-size: 0.78rem; font-weight: 600;
            padding: 3px 8px; border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
        }
        .gl-metric-delta.positive { color: var(--gl-success); background: rgba(16,185,129,0.12); }
        .gl-metric-delta.negative { color: var(--gl-danger);  background: rgba(239,68,68,0.12); }
        .gl-metric-delta.neutral  { color: var(--gl-muted);   background: rgba(255,255,255,0.05); }

        .gl-metric-glow { box-shadow: var(--gl-shadow-card), 0 0 50px rgba(79,140,255,0.25); border-color: rgba(79,140,255,0.4); }

        /* Big "mission-control" prediction tile */
        .gl-prediction {
            position: relative;
            background:
              radial-gradient(600px 240px at 50% -10%, rgba(79,140,255,0.18), transparent 60%),
              var(--gl-surface);
            border: 1px solid rgba(79,140,255,0.28);
            border-radius: 18px;
            padding: 32px 28px;
            text-align: center;
            box-shadow: var(--gl-shadow-card), 0 0 60px rgba(79,140,255,0.18);
        }
        .gl-prediction-label {
            font-family: 'JetBrains Mono', monospace;
            color: var(--gl-primary); font-size: 0.72rem;
            letter-spacing: 0.22em; text-transform: uppercase;
            font-weight: 600;
        }
        .gl-prediction-value {
            font-size: 4.8rem; font-weight: 800; line-height: 1; margin: 14px 0 6px;
            background: linear-gradient(135deg, #FFFFFF, #4F8CFF 80%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -0.04em;
            font-variant-numeric: tabular-nums;
        }
        .gl-prediction-unit { font-size: 1.1rem; color: var(--gl-muted); font-weight: 500; }
        .gl-prediction-sub {
            margin-top: 18px; color: var(--gl-muted); font-size: 0.88rem;
            display: flex; justify-content: center; gap: 18px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Badges */
        .gl-badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 3px 9px; border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em;
            border: 1px solid transparent;
        }
        .gl-badge.blue    { color: #93B8FF; background: rgba(79,140,255,0.12);  border-color: rgba(79,140,255,0.25); }
        .gl-badge.purple  { color: #C4A8FF; background: rgba(124,58,237,0.12); border-color: rgba(124,58,237,0.25); }
        .gl-badge.green   { color: #6EE7B7; background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.25); }
        .gl-badge.amber   { color: #FCD34D; background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.25); }
        .gl-badge.red     { color: #FCA5A5; background: rgba(239,68,68,0.12);  border-color: rgba(239,68,68,0.25); }
        .gl-badge.gray    { color: #CBD5E1; background: rgba(255,255,255,0.05); border-color: var(--gl-border); }

        /* Step / timeline */
        .gl-step {
            position: relative; padding: 18px 20px;
            background: var(--gl-surface);
            border: 1px solid var(--gl-border);
            border-radius: 14px;
            box-shadow: var(--gl-shadow-card);
        }
        .gl-step-num {
            font-family: 'JetBrains Mono', monospace;
            color: var(--gl-primary); font-size: 0.72rem;
            letter-spacing: 0.18em; font-weight: 700;
        }
        .gl-step h3 { margin: 4px 0 8px !important; font-size: 1.1rem !important; }
        .gl-step p { color: #C9D2E1; font-size: 0.9rem; line-height: 1.55; margin: 0; }

        /* Pipeline stage card (Tech Architecture) */
        .gl-stage {
            position: relative;
            background: var(--gl-surface);
            border: 1px solid var(--gl-border);
            border-radius: 12px;
            padding: 16px 14px;
            text-align: center;
            min-height: 120px;
            transition: all 200ms ease;
        }
        .gl-stage:hover { transform: translateY(-3px); border-color: rgba(79,140,255,0.3); }
        .gl-stage-icon {
            width: 36px; height: 36px; border-radius: 9px; margin: 0 auto 10px;
            display: grid; place-items: center;
            background: linear-gradient(135deg, rgba(79,140,255,0.2), rgba(124,58,237,0.2));
            border: 1px solid rgba(79,140,255,0.3);
            font-size: 18px;
        }
        .gl-stage-title { font-size: 0.85rem; font-weight: 600; color: #FFFFFF; }
        .gl-stage-meta { font-size: 0.72rem; color: var(--gl-muted); margin-top: 4px; font-family: 'JetBrains Mono', monospace; }
        .gl-stage.gnn   { border-color: rgba(124,58,237,0.35); box-shadow: 0 0 30px rgba(124,58,237,0.12); }
        .gl-stage.model { border-color: rgba(16,185,129,0.35); box-shadow: 0 0 30px rgba(16,185,129,0.12); }
        .gl-arrow {
            display: grid; place-items: center; height: 120px;
            color: var(--gl-primary); font-size: 22px; opacity: 0.7;
        }

        /* ----- Streamlit widget restyling ----- */
        /* Selectbox / inputs */
        div[data-baseweb="select"] > div,
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background: var(--gl-surface) !important;
            border: 1px solid var(--gl-border) !important;
            border-radius: 10px !important;
            color: var(--gl-text) !important;
            font-family: 'Inter', sans-serif !important;
        }
        div[data-baseweb="select"] > div:hover { border-color: rgba(79,140,255,0.4) !important; }

        /* Slider */
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background: var(--gl-primary) !important;
            box-shadow: 0 0 12px rgba(79,140,255,0.5);
        }

        /* Radio (horizontal pills) */
        div[role="radiogroup"] label {
            background: var(--gl-surface) !important;
            border: 1px solid var(--gl-border) !important;
            border-radius: 8px !important;
            padding: 6px 14px !important;
            margin-right: 6px !important;
            transition: all 150ms;
        }
        div[role="radiogroup"] label:hover { border-color: rgba(79,140,255,0.4) !important; }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--gl-primary), #3B6FE0) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(79,140,255,0.5) !important;
            border-radius: 10px !important;
            padding: 0.55rem 1.2rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            box-shadow: 0 6px 18px -6px rgba(79,140,255,0.5);
            transition: transform 140ms ease, box-shadow 140ms ease;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px -6px rgba(79,140,255,0.7);
        }

        /* Native st.metric tuning (used in Network Explorer profile column) */
        div[data-testid="stMetric"] {
            background: var(--gl-surface);
            border: 1px solid var(--gl-border);
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        div[data-testid="stMetricLabel"] {
            color: var(--gl-muted) !important;
            text-transform: uppercase; letter-spacing: 0.08em;
            font-size: 0.7rem !important; font-weight: 600 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-variant-numeric: tabular-nums;
            font-weight: 700 !important;
        }

        /* DataFrame */
        div[data-testid="stDataFrame"] {
            background: var(--gl-surface);
            border: 1px solid var(--gl-border);
            border-radius: 12px;
            padding: 4px;
        }

        /* Alerts -> glass */
        div[data-testid="stAlert"] {
            background: var(--gl-surface) !important;
            border: 1px solid var(--gl-border) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(12px);
            color: var(--gl-text) !important;
        }

        /* Divider */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, var(--gl-border), transparent) !important;
            margin: 28px 0 !important;
        }

        /* Fade-in animation for page content */
        .main .block-container > div { animation: gl-fade 360ms ease both; }
        @keyframes gl-fade {
            from { opacity: 0; transform: translateY(4px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- Convenience HTML helpers used across pages ----------

def hero(eyebrow: str, title: str, subtitle: str, status: str = "LIVE MODEL",
         status_kind: str = "success", meta: list[str] | None = None) -> None:
    """Render the standardized hero block at the top of each page."""
    color_class = {"success": "", "warning": "warn", "danger": "danger"}.get(status_kind, "")
    meta_html = ""
    if meta:
        meta_html = "".join(f'<span class="gl-meta-chip">{m}</span>' for m in meta)

    st.markdown(
        f"""
        <div class="gl-hero">
          <div class="gl-hero-left">
            <div class="gl-hero-eyebrow">{eyebrow}</div>
            <h1 class="gl-hero-title">{title}</h1>
            <p class="gl-hero-sub">{subtitle}</p>
          </div>
          <div class="gl-hero-right">
            <span class="gl-status {color_class}">● {status}</span>
            <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end;">{meta_html}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(
        f'<div class="gl-section"><h3>{title}</h3><div class="gl-section-rule"></div></div>',
        unsafe_allow_html=True,
    )


def insight(body_html: str, icon: str = "i") -> None:
    """Narrative-first insight card; pass HTML body."""
    st.markdown(
        f'<div class="gl-insight"><div class="gl-insight-icon">{icon}</div>'
        f'<div class="gl-insight-body">{body_html}</div></div>',
        unsafe_allow_html=True,
    )


# Shared Plotly layout (consumed by charts.py and per-page Plotly figs)
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#C9D2E1", size=12),
    title=dict(font=dict(family="Inter, sans-serif", color="#FFFFFF", size=15)),
    legend=dict(
        bgcolor="rgba(17,24,39,0.6)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(color="#C9D2E1", size=11),
    ),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor="rgba(10,16,32,0.95)",
        bordercolor="rgba(79,140,255,0.4)",
        font=dict(family="Inter", color="#FFFFFF", size=12),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(color="#94A3B8"),
        title_font=dict(color="#94A3B8", size=12),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(color="#94A3B8"),
        title_font=dict(color="#94A3B8", size=12),
    ),
)


def apply_plotly_theme(fig, hovermode: str | None = None, height: int | None = None):
    """Apply the global Plotly theme to a figure in-place. Returns the figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    if hovermode:
        fig.update_layout(hovermode=hovermode)
    if height:
        fig.update_layout(height=height)
    return fig
