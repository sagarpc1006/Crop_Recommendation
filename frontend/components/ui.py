"""Reusable UI components and styles for Streamlit frontend."""

import streamlit as st


def inject_custom_css():
    """Inject modern styling into the Streamlit app."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }
            
            .main-header {
                background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
                padding: 2.2rem;
                border-radius: 14px;
                color: white;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            }
            .main-header h1 {
                margin: 0;
                font-size: 2.3rem;
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            .main-header p {
                margin: 0.5rem 0 0 0;
                font-size: 1.05rem;
                opacity: 0.92;
            }

            .status-card {
                padding: 1.2rem;
                border-radius: 10px;
                border: 1px solid #e0e6ed;
                background-color: #ffffff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                margin-bottom: 1rem;
            }
            
            .badge-online {
                background-color: #d1fae5;
                color: #065f46;
                padding: 0.25rem 0.65rem;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
            }
            .badge-offline {
                background-color: #fee2e2;
                color: #991b1b;
                padding: 0.25rem 0.65rem;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
            }
            .badge-warning {
                background-color: #fef3c7;
                color: #92400e;
                padding: 0.25rem 0.65rem;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str):
    """Render the top banner header."""
    st.markdown(
        f"""
        <div class="main-header">
            <h1>🌿 {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(title: str, is_active: bool, detail: str, is_warning: bool = False):
    """Render a connection or service status tile."""
    if is_active:
        badge_class = "badge-online"
        badge_text = "CONNECTED / READY"
    elif is_warning:
        badge_class = "badge-warning"
        badge_text = "ACTION REQUIRED"
    else:
        badge_class = "badge-offline"
        badge_text = "DISCONNECTED"

    st.markdown(
        f"""
        <div class="status-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <strong>{title}</strong>
                <span class="{badge_class}">{badge_text}</span>
            </div>
            <p style="margin: 0; font-size: 0.88rem; color: #555;">{detail}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
