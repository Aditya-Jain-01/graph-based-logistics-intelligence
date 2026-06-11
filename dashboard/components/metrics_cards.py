import streamlit as st

def metric_card(label, value, delta=None, delta_type="neutral"):
    """
    Renders a beautifully styled metric card.
    delta_type: 'positive', 'negative', 'neutral' (determines color)
    """
    if delta_type == "positive":
        delta_html = f'<div class="metric-delta positive">↑ {delta}</div>'
    elif delta_type == "negative":
        delta_html = f'<div class="metric-delta negative">↓ {delta}</div>'
    elif delta:
        delta_html = f'<div class="metric-delta neutral">{delta}</div>'
    else:
        delta_html = ""

    html = f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def badge(text, color="blue"):
    """
    Returns an HTML badge string. Color options: 'red', 'blue', 'green', 'amber'.
    """
    return f'<span class="badge badge-{color}">{text}</span>'
