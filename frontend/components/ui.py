"""
Complete UI component library and design system for GROWIT.

All visual primitives live here so app.py stays clean and declarative.
"""

import streamlit as st
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS & CSS
# ──────────────────────────────────────────────────────────────────────────────

PLANT_FALLBACK_IMAGES: dict[str, str] = {
    "aloe vera":     "🌵",
    "money plant":   "🍀",
    "tulsi":         "🌿",
    "snake plant":   "🌱",
    "marigold":      "🌼",
    "rose":          "🌹",
    "cactus":        "🌵",
    "lavender":      "💜",
    "sunflower":     "🌻",
    "mint":          "🌿",
}

SOIL_ICONS = {"Sandy": "🏜️", "Loamy": "🌍", "Clay": "🧱",
              "Well-drained": "💧", "Peaty": "🍂", "Chalky": "⬜"}
SUNLIGHT_ICONS = {"Full Sun": "☀️", "Partial Shade": "⛅", "Low Light": "🌙",
                  "Bright Indirect": "🌤️"}
WATER_ICONS = {"Low": "💧", "Medium": "💦", "High": "🌊"}
CLIMATE_ICONS = {"Warm/Dry": "🌞", "Humid/Tropical": "🌴", "Warm/Tropical": "🌺",
                 "Warm/Temperate": "🌤️", "Cold/Temperate": "❄️", "Any/Indoor": "🏠",
                 "Tropical": "🌴", "Temperate": "🌤️"}

SCORE_COLORS = {
    (80, 101): ("#065f46", "#d1fae5", "Excellent match"),
    (60,  80): ("#1e3a5f", "#dbeafe", "Good match"),
    (40,  60): ("#713f12", "#fef3c7", "Partial match"),
    (0,   40): ("#7f1d1d", "#fee2e2", "Low match"),
}


def _score_style(score: float) -> tuple[str, str, str]:
    for (lo, hi), (fg, bg, label) in SCORE_COLORS.items():
        if lo <= score < hi:
            return fg, bg, label
    return "#065f46", "#d1fae5", "Excellent match"


def render_html(html: str, *args, **kwargs):
    """Render an HTML block safely in Streamlit without markdown code-block triggers.
    
    Markdown syntax interprets any line with 4+ spaces of indentation as a <pre><code> block.
    Stripping leading indentation from each line guarantees pure, proper HTML rendering.
    """
    clean_lines = [line.strip() for line in html.strip().splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)


def inject_custom_css():
    """Inject the complete GROWIT design system into the Streamlit app."""
    render_html("""
    <style>
    /* ── Google Font ─────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f4f7f4 !important;
        color: #0f3d2e !important;
    }

    /* ── Hide default Streamlit chrome ───────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

    /* ── Form Labels & Controls Contrast Fix ──────────────────────────── */
    div[data-testid="stForm"] {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        border: 1px solid #d4edda !important;
        box-shadow: 0 4px 18px rgba(15,61,46,0.06) !important;
    }
    div[data-testid="stForm"] label,
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p,
    .stSelectbox label,
    .stSlider label,
    .stCheckbox label {
        color: #0f3d2e !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #c8e6c9 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #0f3d2e !important;
        font-weight: 500 !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #1b6b45 0%, #2d9e6b 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(45,158,107,0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #145536 0%, #248257 100%) !important;
        box-shadow: 0 6px 20px rgba(45,158,107,0.45) !important;
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"] {
        border-radius: 10px !important;
        border: 1.5px solid #c8e6c9 !important;
        background-color: white !important;
        color: #0f3d2e !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #f0fdf4 !important;
        border-color: #2d9e6b !important;
        color: #1b6b45 !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3d2e 0%, #1a5c40 100%) !important;
    }
    section[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
    section[data-testid="stSidebar"] .stRadio label { color: #c8e6c9 !important; }
    section[data-testid="stSidebar"] .stDivider { border-color: #2e7d52 !important; }
    section[data-testid="stSidebar"] .stCaption { color: #81c784 !important; }

    /* ── Hero Banner ─────────────────────────────────────────────────── */
    .flora-hero {
        background: linear-gradient(135deg, #0f3d2e 0%, #1b6b45 45%, #2d9e6b 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(15,61,46,0.25);
    }
    .flora-hero::before {
        content: "🌿";
        position: absolute;
        right: 2rem; top: 50%;
        transform: translateY(-50%);
        font-size: 7rem;
        opacity: 0.15;
    }
    .flora-hero h1 {
        font-size: 2.6rem; font-weight: 800;
        margin: 0 0 0.6rem 0; letter-spacing: -1px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .flora-hero p {
        font-size: 1.15rem; margin: 0 0 0.4rem 0; opacity: 0.9;
    }
    .flora-hero .tagline {
        font-size: 0.95rem; opacity: 0.7; font-style: italic;
    }

    /* ── Section headings ─────────────────────────────────────────────── */
    .section-heading {
        display: flex; align-items: center; gap: 0.7rem;
        font-size: 1.4rem; font-weight: 700; color: #0f3d2e;
        margin: 1.8rem 0 1.2rem 0; padding-bottom: 0.6rem;
        border-bottom: 2px solid #d4edda;
    }

    /* ── Stat chips (home page) ───────────────────────────────────────── */
    .stat-row { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0; }
    .stat-chip {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 50px; padding: 0.5rem 1.2rem;
        font-size: 0.9rem; font-weight: 600; color: white;
        backdrop-filter: blur(4px);
    }

    /* ── Feature cards (home page) ────────────────────────────────────── */
    .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0; }
    .feature-card {
        background: white; border-radius: 14px; padding: 1.4rem 1.2rem;
        border: 1px solid #e8f5e9; text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.09); }
    .feature-card .icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
    .feature-card h3 { font-size: 1rem; font-weight: 700; color: #0f3d2e; margin: 0 0 0.4rem; }
    .feature-card p { font-size: 0.85rem; color: #555; margin: 0; line-height: 1.5; }

    /* ── Plant card ────────────────────────────────────────────────────── */
    .plant-card {
        background: white; border-radius: 16px;
        border: 1px solid #e8f5e9;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        overflow: hidden; transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .plant-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .plant-card-image {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        height: 140px; display: flex; align-items: center;
        justify-content: center; font-size: 4rem;
        border-bottom: 1px solid #e0ede0;
    }
    .plant-card-body { padding: 1.1rem; }
    .plant-card-name {
        font-size: 1.05rem; font-weight: 700; color: #0f3d2e;
        margin: 0 0 0.5rem; line-height: 1.3;
    }
    .score-badge {
        display: inline-flex; align-items: center; gap: 0.3rem;
        border-radius: 50px; padding: 0.3rem 0.8rem;
        font-size: 0.8rem; font-weight: 700; margin-bottom: 0.8rem;
    }
    .score-bar-wrap { background: #f0f0f0; border-radius: 99px; height: 6px; margin-bottom: 0.9rem; }
    .score-bar { height: 6px; border-radius: 99px; }
    .plant-meta { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 0.9rem; }
    .plant-meta-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; color: #444; }
    .plant-meta-label { font-weight: 600; color: #0f3d2e; min-width: 80px; }

    /* ── Detail panel ────────────────────────────────────────────────── */
    .detail-panel {
        background: white; border-radius: 18px;
        border: 1px solid #e8f5e9; padding: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }
    .detail-image {
        background: linear-gradient(135deg, #e8f5e9, #a5d6a7);
        border-radius: 14px; height: 200px;
        display: flex; align-items: center;
        justify-content: center; font-size: 6rem;
        margin-bottom: 1.2rem;
    }
    .detail-chip {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: #f0f9f4; border: 1px solid #c8e6c9;
        border-radius: 50px; padding: 0.35rem 0.85rem;
        font-size: 0.82rem; font-weight: 600; color: #1b5e20;
        margin: 0.25rem;
    }

    /* ── Requirements grid & cards ────────────────────────────────────── */
    .req-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.85rem;
        margin: 1.2rem 0;
    }
    .req-card {
        background: white;
        border: 1px solid #e2ece2;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .req-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    .req-card-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748b;
        margin-bottom: 0.35rem;
    }
    .req-card-val {
        font-size: 0.98rem;
        font-weight: 700;
        color: #0f3d2e;
    }
    .info-section-card {
        background: white;
        border: 1px solid #e8f5e9;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }

    /* ── Search card ─────────────────────────────────────────────────── */
    .search-result-card {
        background: white; border-radius: 12px;
        border: 1px solid #e8f5e9; padding: 1rem 1.2rem;
        margin-bottom: 0.8rem; cursor: pointer;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .search-result-card:hover { border-color: #66bb6a; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

    /* ── Care guide card ──────────────────────────────────────────────── */
    .care-card {
        background: white; border-radius: 14px;
        border-left: 4px solid #2d9e6b; padding: 1.2rem 1.4rem;
        margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    .care-card h4 { color: #0f3d2e; margin: 0 0 0.5rem; font-size: 1rem; font-weight: 700; }
    .care-card p  { color: #444; margin: 0; font-size: 0.88rem; line-height: 1.6; }
    .care-tip { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px;
                padding: 0.7rem 1rem; margin: 0.4rem 0; font-size: 0.85rem; color: #166534; }

    /* ── History table ────────────────────────────────────────────────── */
    .history-row {
        background: white; border-radius: 10px; padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem; border: 1px solid #e8f5e9;
        display: flex; align-items: center; gap: 1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }
    .score-pill {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 0.3rem 0.75rem; border-radius: 99px;
        font-weight: 700; font-size: 0.88rem;
    }
    .score-high { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .score-mid  { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .score-low  { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .history-card-box {
        background: white; border-radius: 14px;
        border: 1px solid #e8f5e9; padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        margin-bottom: 1rem; height: 100%;
        display: flex; flex-direction: column; justify-content: space-between;
    }


    /* ── Status badges ────────────────────────────────────────────────── */
    .badge { display: inline-flex; align-items: center; gap: 0.3rem;
             border-radius: 50px; padding: 0.25rem 0.7rem;
             font-size: 0.78rem; font-weight: 600; }
    .badge-green  { background:#d1fae5; color:#065f46; }
    .badge-red    { background:#fee2e2; color:#991b1b; }
    .badge-yellow { background:#fef3c7; color:#92400e; }
    .badge-blue   { background:#dbeafe; color:#1e3a5f; }

    /* ── CTA Button override ──────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0f3d2e, #2d9e6b) !important;
        border: none !important; border-radius: 50px !important;
        font-weight: 700 !important; font-size: 1rem !important;
        padding: 0.6rem 2rem !important; letter-spacing: 0.3px !important;
        box-shadow: 0 4px 14px rgba(15,61,46,0.3) !important;
    }

    /* ── Form inputs ──────────────────────────────────────────────────── */
    .stSelectbox > div > div, .stRadio > div { border-radius: 10px !important; }

    /* ── Divider ──────────────────────────────────────────────────────── */
    hr { border-color: #e0ede0 !important; }

    /* ── Status card ──────────────────────────────────────────────────── */
    .status-card {
        padding: 1rem; border-radius: 10px; border: 1px solid #e0ede0;
        background: rgba(255,255,255,0.08); margin-bottom: 0.8rem;
    }
    .status-card strong { color: #e8f5e9 !important; }
    .status-card p { color: #a5d6a7 !important; font-size: 0.83rem; margin: 0.3rem 0 0; }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HEADER / HERO
# ──────────────────────────────────────────────────────────────────────────────

def render_hero(show_cta: bool = False):
    """Render the main hero banner. Returns True if CTA was clicked."""
    render_html("""
    <div class="flora-hero">
        <h1>🌿 GROWIT</h1>
        <p>Find the Right Plant for Your Space</p>
        <p class="tagline">Smart recommendations based on your soil, climate, sunlight & space.</p>
        <div class="stat-row">
            <span class="stat-chip">🌱 30+ Plant Species</span>
            <span class="stat-chip">🧪 Transparent Scoring</span>
            <span class="stat-chip">🌐 External API Enrichment</span>
        </div>
    </div>
    """)
    if show_cta:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            return st.button("🌱 Find My Plant", type="primary", use_container_width=True)
    return False


def render_header(title: str, subtitle: str):
    """Compact header for non-home pages."""
    render_html(f"""
    <div class="flora-hero" style="padding:1.8rem 2rem;">
        <h1 style="font-size:1.8rem">🌿 {title}</h1>
        <p style="font-size:0.95rem">{subtitle}</p>
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION HEADING
# ──────────────────────────────────────────────────────────────────────────────

def section_heading(icon: str, title: str):
    st.markdown(f'<div class="section-heading"><span>{icon}</span>{title}</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR STATUS
# ──────────────────────────────────────────────────────────────────────────────

def render_status_card(title: str, is_active: bool, detail: str, is_warning: bool = False):
    if is_active:
        badge = '<span class="badge badge-green">● ONLINE</span>'
    elif is_warning:
        badge = '<span class="badge badge-yellow">⚠ WARNING</span>'
    else:
        badge = '<span class="badge badge-red">✕ OFFLINE</span>'

    st.markdown(f"""
    <div class="status-card">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <strong style="font-size:0.9rem">{title}</strong>{badge}
        </div>
        <p>{detail}</p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PLANT EMOJI FALLBACK
# ──────────────────────────────────────────────────────────────────────────────

def _plant_emoji(name: str) -> str:
    name_lower = name.lower()
    for key, emoji in PLANT_FALLBACK_IMAGES.items():
        if key in name_lower:
            return emoji
    return "🌿"


# ──────────────────────────────────────────────────────────────────────────────
# PLANT CARD
# ──────────────────────────────────────────────────────────────────────────────

def render_plant_card(
    plant: dict,
    score: float | int | None = None,
    matched: list | None = None,
    unmatched: list | None = None,
    show_score: bool | None = None,
    on_details = None,
    key_suffix: str = ""
):
    """Render a rich, interactive plant card for recommendations or search results."""
    name     = plant.get("name", "Unknown Plant")
    sci_name = plant.get("scientific_name") or plant.get("scientificName")
    care     = plant.get("basic_care") or {}
    soil     = plant.get("soil_type") or care.get("soil_type") or "—"
    climate  = plant.get("climate") or care.get("climate") or "—"
    sunlight = plant.get("sunlight") or care.get("sunlight") or "—"
    water    = plant.get("water_needs") or care.get("water_needs") or "—"
    space    = plant.get("space_requirement") or care.get("space_requirement") or "—"
    img_url  = plant.get("image_url") or plant.get("thumbnail_url")
    source   = plant.get("source", "local")
    emoji    = _plant_emoji(name)

    # Determine whether to show recommendation score
    if show_score is None:
        raw_score = score if score is not None else plant.get("compatibility_score")
        show_score = bool(raw_score is not None and raw_score > 0)

    # Image section with graceful error fallback
    if img_url:
        img_html = (
            f'<div style="width:100%;height:150px;overflow:hidden;background:#e8f5e9;position:relative;">'
            f'<img src="{img_url}" alt="{name}" style="width:100%;height:150px;object-fit:cover;display:block;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';" />'
            f'<div class="plant-card-image" style="height:150px;display:none;align-items:center;justify-content:center;font-size:3.5rem;background:#e8f5e9;">{emoji}</div>'
            f'</div>'
        )
    else:
        img_html = f'<div class="plant-card-image" style="height:150px;display:flex;align-items:center;justify-content:center;font-size:3.5rem;background:#e8f5e9;">{emoji}</div>'

    # Score or Badge header
    if show_score:
        score_val = score if score is not None else plant.get("compatibility_score", 0)
        score_pct = round(score_val * 100 if isinstance(score_val, float) and score_val <= 1 else (score_val or 0))
        fg, bg, label = _score_style(score_pct)
        score_width = min(score_pct, 100)
        score_color = "#2d9e6b" if score_pct >= 70 else "#f59e0b" if score_pct >= 45 else "#ef4444"

        score_html = (
            f'<div style="margin-bottom:0.8rem;">'
            f'<span class="score-badge" style="background:{bg};color:{fg};display:inline-flex;padding:0.25rem 0.75rem;border-radius:50px;font-weight:700;font-size:0.8rem;">★ {score_pct}% &nbsp;{label}</span>'
            f'<div class="score-bar-wrap" style="background:#f0f0f0;border-radius:99px;height:6px;margin-top:0.4rem;overflow:hidden;">'
            f'<div class="score-bar" style="width:{score_width}%;background:{score_color};height:6px;border-radius:99px;"></div>'
            f'</div></div>'
        )
    else:
        src_label = "🌐 External API" if source != "local" else "🗄️ Botanical Database"
        src_cls   = "badge-blue" if source != "local" else "badge-green"
        score_html = f'<div style="margin-bottom:0.75rem"><span class="badge {src_cls}">{src_label}</span></div>'

    # Matched / Unmatched factors & Why Recommended
    factors_html = ""
    if matched or unmatched:
        factors_html += '<div style="font-size:0.78rem;font-weight:700;color:#0f3d2e;margin-top:0.4rem;margin-bottom:0.2rem">💡 Why Recommended:</div>'
    if matched:
        factors_html += "".join(
            f'<span class="detail-chip" style="font-size:0.73rem;margin:0.12rem;background:#f0fdf4;border:1px solid #bbf7d0;color:#166534;border-radius:50px;padding:0.18rem 0.55rem;display:inline-block;">✓ {m}</span>'
            for m in matched[:2]
        )
    if unmatched:
        factors_html += "".join(
            f'<span class="detail-chip" style="font-size:0.73rem;margin:0.12rem;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;border-radius:50px;padding:0.18rem 0.55rem;display:inline-block;">⚠️ {u}</span>'
            for u in unmatched[:1]
        )

    sci_name_html = f'<div style="font-size:0.82rem;color:#4a7c59;font-style:italic;margin-top:-0.3rem;margin-bottom:0.5rem;">{sci_name}</div>' if sci_name else ""

    meta_html = (
        f'<div class="plant-meta" style="display:flex;flex-direction:column;gap:0.35rem;margin-bottom:0.9rem;">'
        f'<div class="plant-meta-row" style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:#444;">{SOIL_ICONS.get(soil,"🌍")} <span class="plant-meta-label" style="font-weight:600;color:#0f3d2e;min-width:70px;">Soil</span>{soil}</div>'
        f'<div class="plant-meta-row" style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:#444;">{SUNLIGHT_ICONS.get(sunlight,"☀️")} <span class="plant-meta-label" style="font-weight:600;color:#0f3d2e;min-width:70px;">Sunlight</span>{sunlight}</div>'
        f'<div class="plant-meta-row" style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:#444;">{WATER_ICONS.get(water,"💧")} <span class="plant-meta-label" style="font-weight:600;color:#0f3d2e;min-width:70px;">Water</span>{water}</div>'
        f'<div class="plant-meta-row" style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:#444;">{CLIMATE_ICONS.get(climate,"🌡️")} <span class="plant-meta-label" style="font-weight:600;color:#0f3d2e;min-width:70px;">Climate</span>{climate}</div>'
        f'<div class="plant-meta-row" style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:#444;">📐 <span class="plant-meta-label" style="font-weight:600;color:#0f3d2e;min-width:70px;">Space</span>{space}</div>'
        f'</div>'
    )

    card_html = (
        f'<div class="plant-card">'
        f'{img_html}'
        f'<div class="plant-card-body">'
        f'<div class="plant-card-name" style="font-size:1.05rem;font-weight:700;color:#0f3d2e;margin:0 0 0.3rem;">{emoji} {name}</div>'
        f'{sci_name_html}'
        f'{score_html}'
        f'{meta_html}'
        f'{"<div style=\'margin-top:0.4rem;\'>" + factors_html + "</div>" if factors_html else ""}'
        f'</div>'
        f'</div>'
    )
    render_html(card_html)

    if on_details:
        btn_key = f"card_details_{plant.get('plant_id', name)}_{key_suffix}"
        if st.button("🔍 View Details", key=btn_key, use_container_width=True):
            on_details(plant)


def render_empty_state(criteria: dict):
    """Render friendly empty result state with criteria explanation and suggestions."""
    soil = criteria.get("soil_type", "—")
    climate = criteria.get("climate", "—")
    sunlight = criteria.get("sunlight", "—")
    space = criteria.get("space", "—")
    render_html(f"""
    <div style="text-align:center;padding:2.5rem 1.5rem;background:#fbfbfb;border-radius:16px;border:1px dashed #d0d7de;margin:1rem 0;">
        <div style="font-size:3.5rem;margin-bottom:0.6rem">🌱</div>
        <h3 style="color:#0f3d2e;margin-bottom:0.4rem;font-size:1.2rem">No Matching Plants Found</h3>
        <p style="color:#666;font-size:0.9rem;max-width:460px;margin:0 auto 1.2rem auto;line-height:1.5">
            We couldn't find any varieties matching your exact combination of:<br>
            <strong>{soil}</strong> soil · <strong>{climate}</strong> climate · <strong>{sunlight}</strong> · <strong>{space}</strong> space.
        </p>
        <div style="background:#e8f5e9;border-radius:10px;padding:0.8rem 1.2rem;display:inline-block;text-align:left;font-size:0.85rem;color:#1b5e20;">
            💡 <strong>Suggestions to find more plants:</strong><br>
            • Try selecting <em>Partial Shade</em> or <em>Full Sun</em>.<br>
            • Try <em>Warm/Dry</em> or <em>Humid/Tropical</em> for climate.<br>
            • Allow more space or adjust soil texture.
        </div>
    </div>
    """)


def render_error_state(error_type: str, message: str):
    """Render styled error card for backend unavailable, timeout, or server error."""
    if error_type == "backend_unavailable":
        title = "⚠️ Flask Recommendation Backend Offline"
        desc = (
            "Could not reach the Flask recommendation API at <code>http://localhost:5000</code>.<br>"
            "Please start the Flask backend server in your terminal:"
        )
        code_snip = "python backend/app.py"
    elif error_type == "timeout":
        title = "⏱️ Recommendation Request Timed Out"
        desc = (
            "The Flask recommendation engine took longer than expected to compute matches.<br>"
            "The backend may still be starting up or under heavy load."
        )
        code_snip = None
    else:
        title = "❌ Recommendation Error"
        desc = message or "An unexpected error occurred while communicating with the backend."
        code_snip = None

    render_html(f"""
    <div style="background:#fff5f5;border:1px solid #fed7d7;border-radius:14px;padding:1.2rem 1.4rem;margin:1rem 0;">
        <h4 style="color:#c53030;margin:0 0 0.4rem 0;display:flex;align-items:center;gap:0.5rem;font-size:1rem">
            {title}
        </h4>
        <p style="color:#4a5568;font-size:0.88rem;margin:0;line-height:1.5">
            {desc}
        </p>
    </div>
    """)
    if code_snip:
        st.code(code_snip, language="bash")



# ──────────────────────────────────────────────────────────────────────────────
# PLANT DETAIL PANEL
# ──────────────────────────────────────────────────────────────────────────────

def render_plant_detail(plant: dict, score_data: dict | None = None):
    """Full-width detailed plant view showing all botanical requirements and care advice."""
    name        = plant.get("name", "Unknown Plant")
    sci_name    = plant.get("scientific_name")
    care        = plant.get("basic_care") or {}
    soil        = plant.get("soil_type") or care.get("soil_type") or "Not specified"
    climate     = plant.get("climate") or care.get("climate") or "Not specified"
    sunlight    = plant.get("sunlight") or care.get("sunlight") or "Not specified"
    water       = plant.get("water_needs") or care.get("water_needs") or "Medium"
    space       = plant.get("space_requirement") or care.get("space_requirement") or "Moderate"
    description = plant.get("description") or "Detailed botanical information for this specimen is available in the catalog."
    img_url     = plant.get("image_url") or plant.get("thumbnail_url")
    emoji       = _plant_emoji(name)
    enriched    = plant.get("external_enriched", False)
    ext_source  = plant.get("external_source", "Perenual API")

    # 1. Hero / Header
    col_img, col_info = st.columns([1, 1.8], gap="large")

    with col_img:
        if img_url:
            st.image(img_url, use_container_width=True)
        else:
            st.markdown(f'<div class="detail-image">{emoji}</div>', unsafe_allow_html=True)

        # Status & Safety Badges below image
        badge_list = []
        if enriched:
            badge_list.append(f'<span class="badge badge-blue">🌐 Enriched via {ext_source.title()}</span>')
        else:
            badge_list.append('<span class="badge badge-green">🗄️ Curated Botanical Database</span>')

        if plant.get("indoor_suitable") is True:
            badge_list.append('<span class="badge badge-green">🏠 Indoor Suitable</span>')
        elif plant.get("indoor_suitable") is False:
            badge_list.append('<span class="badge badge-yellow">🌳 Outdoor Preferred</span>')

        if plant.get("poisonous_to_pets") is True:
            badge_list.append('<span class="badge badge-red">⚠️ Toxic to Pets</span>')
        elif plant.get("poisonous_to_pets") is False:
            badge_list.append('<span class="badge badge-green">🐾 Pet Safe</span>')

        st.markdown(
            f'<div style="display:flex;gap:0.4rem;flex-wrap:wrap;margin-top:0.6rem">{"".join(badge_list)}</div>',
            unsafe_allow_html=True
        )

    with col_info:
        st.markdown(f"<h1 style='color:#0f3d2e;margin:0 0 0.2rem 0;'>{emoji} {name}</h1>", unsafe_allow_html=True)
        if sci_name:
            st.markdown(f"<p style='color:#4a7c59;font-style:italic;font-size:1.05rem;margin:0 0 1rem 0;'>{sci_name}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        # Recommendation Compatibility Score Banner (if navigated from recommendation)
        if score_data:
            score_pct = score_data.get("score_pct") if score_data.get("score_pct") is not None else score_data.get("score", 0)
            fg, bg, label = _score_style(score_pct)
            render_html(f"""
            <div style="background:{bg};color:{fg};border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:1rem;border:1px solid rgba(0,0,0,0.06)">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <strong>🎯 Recommendation Match: {score_pct}%</strong>
                    <span style="font-size:0.85rem;font-weight:700">{label}</span>
                </div>
                <div style="background:rgba(0,0,0,0.08);border-radius:99px;height:8px;margin-top:0.6rem">
                    <div style="width:{min(score_pct,100)}%;background:{fg};height:8px;border-radius:99px"></div>
                </div>
            </div>
            """)

            matched   = score_data.get("matched_factors") if score_data.get("matched_factors") is not None else score_data.get("matched", [])
            unmatched = score_data.get("unmatched_factors") if score_data.get("unmatched_factors") is not None else score_data.get("unmatched", [])
            if matched or unmatched:
                mc, uc = st.columns(2)
                with mc:
                    if matched:
                        st.markdown("**✅ Matching Conditions:**")
                        for m in matched:
                            st.markdown(f'<div class="care-tip">✓ {m}</div>', unsafe_allow_html=True)
                with uc:
                    if unmatched:
                        st.markdown("**⚠️ Considerations:**")
                        for u in unmatched:
                            st.markdown(f'<div class="care-tip" style="background:#fff7ed;border-color:#fed7aa;color:#9a3412">✗ {u}</div>', unsafe_allow_html=True)

        # Botanical Overview
        render_html(f"""
        <div class="info-section-card">
            <h4 style="color:#0f3d2e;margin:0 0 0.5rem 0;font-size:1.05rem">📖 Botanical Overview</h4>
            <p style="color:#374151;line-height:1.65;font-size:0.92rem;margin:0">{description}</p>
        </div>
        """)

    # 2. Environmental Requirements Grid (5 Key Cards)
    st.markdown("<h3 style='color:#0f3d2e;margin:1.5rem 0 0.8rem 0;'>🌾 Environmental & Growing Requirements</h3>", unsafe_allow_html=True)

    reqs = [
        ("🌍", "Soil Requirements", soil, "Texture & drainage"),
        ("☀️", "Sunlight Requirements", sunlight, "Daily light exposure"),
        ("💧", "Water Requirements", water, "Moisture needs"),
        ("🌡️", "Climate Zone", climate, "Optimal atmosphere"),
        ("📐", "Space Requirements", space, "Footprint & layout"),
    ]

    req_cols = st.columns(5)
    for col, (ic, title, val, sub) in zip(req_cols, reqs):
        with col:
            render_html(f"""
            <div class="req-card">
                <div style="font-size:1.6rem;margin-bottom:0.3rem">{ic}</div>
                <div class="req-card-label">{title}</div>
                <div class="req-card-val">{val}</div>
                <div style="font-size:0.75rem;color:#64748b;margin-top:0.2rem">{sub}</div>
            </div>
            """)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # 3. Care Instructions, Maintenance & Fertilizer
    care_col1, care_col2 = st.columns(2, gap="large")

    with care_col1:
        watering_freq = plant.get("watering_frequency") or (
            "Allow top 1-2 inches of soil to dry between waterings." if water == "Low"
            else "Keep soil moderately and consistently moist." if water == "Medium"
            else "Water frequently to maintain high root zone moisture."
        )
        pruning_info = plant.get("pruning_notes") or "Prune yellowing or spent leaves in spring to promote healthy, vigorous growth."

        st.markdown(f"""
        <div class="info-section-card">
            <h4 style="color:#0f3d2e;margin:0 0 0.8rem 0;font-size:1.05rem">📋 Care Instructions & Maintenance</h4>
            <div style="margin-bottom:0.8rem">
                <strong style="color:#1b5e20;font-size:0.88rem">💧 Watering Schedule:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">{watering_freq}</p>
            </div>
            <div style="margin-bottom:0.8rem">
                <strong style="color:#1b5e20;font-size:0.88rem">✂️ Pruning & Trimming:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">{pruning_info}</p>
            </div>
            <div>
                <strong style="color:#1b5e20;font-size:0.88rem">☀️ Light & Placement:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">
                    Position in {sunlight.lower()} spot sheltered from severe draft. Rotate pot monthly for balanced foliage development.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with care_col2:
        fertilizer_info = plant.get("fertilizer_notes") or (
            "Feed monthly during active spring/summer growing season with a diluted organic balanced fertilizer (e.g. 10-10-10). Avoid fertilizing in winter dormancy."
        )
        hardiness = plant.get("hardiness_zone") or "Adapts across temperate and indoor climate ranges (Zones 8-11)"

        st.markdown(f"""
        <div class="info-section-card">
            <h4 style="color:#0f3d2e;margin:0 0 0.8rem 0;font-size:1.05rem">🌱 Fertilizer & Nutrition Information</h4>
            <div style="margin-bottom:0.8rem">
                <strong style="color:#1b5e20;font-size:0.88rem">🧪 Fertilizer Guidance:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">{fertilizer_info}</p>
            </div>
            <div style="margin-bottom:0.8rem">
                <strong style="color:#1b5e20;font-size:0.88rem">🗺️ Hardiness & Climate Resilience:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">{hardiness}</p>
            </div>
            <div>
                <strong style="color:#1b5e20;font-size:0.88rem">🌐 External Botanical Metadata:</strong>
                <p style="color:#444;font-size:0.86rem;margin:0.2rem 0 0 0;line-height:1.5">
                    {'Verified with live external Perenual plant index.' if enriched else 'Botanical data verified from local database catalog.'}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SEARCH RESULT ROW
# ──────────────────────────────────────────────────────────────────────────────

def render_search_row(plant: dict, key_suffix: str = "") -> bool:
    """Compact search result row. Returns True if 'View' clicked."""
    name    = plant.get("name", "Unknown")
    soil    = plant.get("soil_type", "—")
    climate = plant.get("climate", "—")
    sun     = plant.get("sunlight", "—")
    source  = plant.get("source", "local")
    emoji   = _plant_emoji(name)
    src_badge = (f'<span class="badge badge-blue">🌐 {source.title()}</span>'
                 if source != "local" else '<span class="badge badge-green">🗄️ Local</span>')

    st.markdown(f"""
    <div class="search-result-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <strong style="font-size:1rem;color:#0f3d2e">{emoji} {name}</strong>
                {src_badge}
                <div style="margin-top:0.4rem;font-size:0.83rem;color:#555">
                    {SOIL_ICONS.get(soil,'🌍')} {soil} &nbsp;•&nbsp;
                    {SUNLIGHT_ICONS.get(sun,'☀️')} {sun} &nbsp;•&nbsp;
                    {CLIMATE_ICONS.get(climate,'🌡️')} {climate}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return st.button("View Details →", key=f"view_{name}_{key_suffix}",
                     use_container_width=False)


# ──────────────────────────────────────────────────────────────────────────────
# CARE GUIDE CARDS
# ──────────────────────────────────────────────────────────────────────────────

CARE_GUIDE_DATA = [
    {
        "icon": "💧",
        "title": "Watering Wisdom",
        "body": "Most indoor plants need water only when the top inch of soil is dry. "
                "Overwatering is the #1 killer of houseplants — less is usually more.",
        "tips": [
            "Check soil moisture with your finger before watering.",
            "Use room-temperature water to avoid shocking roots.",
            "Drain excess water from saucers within 30 minutes.",
        ],
        "plants": ["Snake Plant", "Aloe Vera", "Money Plant"],
    },
    {
        "icon": "☀️",
        "title": "Light Requirements",
        "body": "Light is the engine of plant growth. Matching your plant to the right "
                "light level is crucial — too much or too little both cause problems.",
        "tips": [
            "South-facing windows get the most sun (Full Sun plants).",
            "East/west windows suit Partial Shade plants perfectly.",
            "Use a grow light if you have no natural light available.",
        ],
        "plants": ["Tulsi", "Marigold", "Aloe Vera"],
    },
    {
        "icon": "🌍",
        "title": "Soil Selection",
        "body": "Different plants evolved in different soils. Using the right mix "
                "dramatically improves growth, drainage, and nutrient availability.",
        "tips": [
            "Sandy soil drains fast — ideal for succulents and cacti.",
            "Loamy soil holds moisture well — great for vegetables and herbs.",
            "Add perlite to any mix to improve aeration and drainage.",
        ],
        "plants": ["Money Plant", "Tulsi", "Marigold"],
    },
    {
        "icon": "🌡️",
        "title": "Climate & Temperature",
        "body": "Most tropical houseplants thrive at 18–27°C. "
                "Avoid placing plants near cold drafts or heating vents.",
        "tips": [
            "Keep indoor plants away from air-conditioner vents in summer.",
            "Group plants together in winter — they create their own microclimate.",
            "Tropical plants hate temperatures below 10°C.",
        ],
        "plants": ["Tulsi", "Money Plant", "Snake Plant"],
    },
    {
        "icon": "🌿",
        "title": "Fertilising Basics",
        "body": "Plants need nutrients to grow, but over-fertilising causes salt "
                "build-up and leaf burn. Feed lightly and regularly during the growing season.",
        "tips": [
            "Fertilise spring–summer at half the recommended dose.",
            "Use a balanced NPK fertiliser (e.g. 10-10-10) for most plants.",
            "Never fertilise a stressed or recently repotted plant.",
        ],
        "plants": ["Marigold", "Tulsi", "Money Plant"],
    },
    {
        "icon": "🪴",
        "title": "Repotting Guide",
        "body": "Plants need repotting when roots start escaping the drainage holes "
                "or the soil dries out too quickly between waterings.",
        "tips": [
            "Repot in spring when growth naturally accelerates.",
            "Choose a pot only 2–4 cm larger than the current one.",
            "Water thoroughly after repotting to settle the new soil.",
        ],
        "plants": ["Snake Plant", "Aloe Vera", "Money Plant"],
    },
]


def render_care_guide():
    """Render the full care guide section with all cards."""
    section_heading("🌿", "Plant Care Guide")
    st.markdown(
        '<p style="color:#555;margin-bottom:1.5rem">Essential care knowledge for healthy, thriving plants.</p>',
        unsafe_allow_html=True
    )

    # Category filter
    categories = ["All Topics"] + [c["title"] for c in CARE_GUIDE_DATA]
    selected = st.selectbox("Filter by topic:", categories, label_visibility="collapsed")

    guides = CARE_GUIDE_DATA if selected == "All Topics" else [
        c for c in CARE_GUIDE_DATA if c["title"] == selected
    ]

    for guide in guides:
        with st.expander(f"{guide['icon']} {guide['title']}", expanded=(selected != "All Topics")):
            st.markdown(f'<div class="care-card"><p>{guide["body"]}</p></div>',
                        unsafe_allow_html=True)
            st.markdown("**💡 Quick Tips**")
            for tip in guide["tips"]:
                st.markdown(f'<div class="care-tip">→ {tip}</div>',
                            unsafe_allow_html=True)
            st.markdown(
                "**🌱 Great for:** " + "  ".join(
                    f'`{p}`' for p in guide["plants"]
                )
            )


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE CARDS  (home page)
# ──────────────────────────────────────────────────────────────────────────────

def render_feature_cards():
    FEATURES = [
        ("🧪", "Transparent Scoring", "Compatibility score explained factor-by-factor — no black-box AI."),
        ("🌐", "External Enrichment", "Real images and care data pulled from the Perenual Plant API."),
        ("🗄️", "PostgreSQL Backed", "Plant catalog stored in a relational database with full-text search."),
        ("🌱", "30+ Curated Plants", "Comprehensive botanical catalog covering indoor plants, herbs, flowers, succulents and more."),
        ("⚡", "Fast Recommendations", "Weighted scoring engine returns results in under 100 ms."),
        ("📖", "Care Guides", "Built-in watering, light, soil, and fertilising guidance for every plant."),
    ]
    html = '<div class="feature-grid">'
    for icon, title, desc in FEATURES:
        html += f"""
        <div class="feature-card">
            <div class="icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# RECOMMENDATION HISTORY
# ──────────────────────────────────────────────────────────────────────────────

def render_history(history: list[dict]):
    """Render session-based recommendation history."""
    if not history:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#888">
            <div style="font-size:3rem;margin-bottom:1rem">🕒</div>
            <strong>No history yet</strong><br>
            <span>Your recommendation searches will appear here.</span>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, entry in enumerate(reversed(history)):
        criteria = entry.get("criteria", {})
        results  = entry.get("results", [])
        ts       = entry.get("timestamp", "")
        n        = len(results)
        top      = results[0].get("plant", {}).get("name", "—") if results else "—"

        emoji_map = {
            "soil_type": SOIL_ICONS.get(criteria.get("soil_type", ""), "🌍"),
            "sunlight":  SUNLIGHT_ICONS.get(criteria.get("sunlight", ""), "☀️"),
        }

        st.markdown(f"""
        <div class="history-row">
            <div style="font-size:2rem">🔍</div>
            <div style="flex:1">
                <strong style="color:#0f3d2e">Search #{len(history) - i}</strong>
                <span style="font-size:0.8rem;color:#888;margin-left:0.5rem">{ts}</span><br>
                <span style="font-size:0.85rem;color:#444">
                    {emoji_map['soil_type']} {criteria.get('soil_type','—')} &nbsp;•&nbsp;
                    {criteria.get('climate','—')} &nbsp;•&nbsp;
                    {emoji_map['sunlight']} {criteria.get('sunlight','—')} &nbsp;•&nbsp;
                    {criteria.get('space','—')}
                </span>
            </div>
            <div style="text-align:right">
                <span class="badge badge-green">{n} match{'es' if n!=1 else ''}</span><br>
                <span style="font-size:0.82rem;color:#555;margin-top:0.2rem">Top: {top}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if results and st.button(f"↩ Re-run this search", key=f"rerun_{i}"):
            return criteria  # caller should re-run

    return None


def format_history_date(ts: str | None) -> tuple[str, str]:
    """Parse timestamp into (date_display, time_display), e.g. ('21 Sep', '2026, 22:30')."""
    if not ts:
        return ("—", "")
    try:
        clean_ts = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_ts)
        return (dt.strftime("%d %b"), dt.strftime("%Y, %H:%M"))
    except Exception:
        parts = str(ts).split("T")
        if len(parts) == 2:
            return (parts[0], parts[1][:5])
        return (str(ts)[:10], str(ts)[11:16] if len(str(ts)) > 16 else "")


def render_history_empty_state():
    """Render friendly empty state when no recommendation history exists."""
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 1.5rem;background:white;border-radius:18px;border:1px solid #e8f5e9;box-shadow:0 4px 20px rgba(0,0,0,0.04);margin:1.5rem 0">
        <div style="font-size:3.5rem;margin-bottom:0.8rem">🌱📜</div>
        <h3 style="color:#0f3d2e;margin:0 0 0.5rem;font-weight:700">No Recommendation History Yet</h3>
        <p style="color:#64748b;max-width:480px;margin:0 auto 1.5rem;line-height:1.6;font-size:0.95rem">
            You haven't generated any plant recommendations yet. Choose your soil, climate, sunlight, and space criteria to discover tailored plant matches!
        </p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🌱 Discover Your First Plants", type="primary", use_container_width=True, key="btn_empty_history_cta"):
            st.session_state.page = "🌱 Recommendations"
            st.rerun()


def render_my_history_table(recommendations: list[dict]):
    """Render previous recommendations as a clean, interactive table matching:

    Date        Plant          Score
    --------------------------------
    21 Sep      Aloe Vera     94%
    20 Sep      Snake Plant   88%

    Allows user to view previous recommendation details or open plant details.
    """
    if not recommendations:
        render_history_empty_state()
        return

    st.markdown(f"""
    <div style="margin-bottom:0.8rem;color:#64748b;font-size:0.88rem;display:flex;align-items:center;justify-content:space-between">
        <span>Displaying <strong>{len(recommendations)}</strong> recommendation record{'s' if len(recommendations) != 1 else ''}</span>
        <span style="font-size:0.8rem;color:#166534;background:#f0fdf4;padding:0.2rem 0.6rem;border-radius:99px;border:1px solid #bbf7d0">
            🗄️ Stored in PostgreSQL
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Table Header
    header_cols = st.columns([2, 4, 2, 3, 3])
    with header_cols[0]:
        st.markdown("**Date**")
    with header_cols[1]:
        st.markdown("**Plant**")
    with header_cols[2]:
        st.markdown("**Score**")
    with header_cols[3]:
        st.markdown("**Preferences**")
    with header_cols[4]:
        st.markdown("**Actions**")

    st.divider()

    for idx, rec in enumerate(recommendations):
        plant = rec.get("plant") or {}
        plant_name = plant.get("name") or rec.get("name") or "Unknown Plant"
        sci_name = plant.get("scientific_name") or plant.get("scientificName") or ""
        score_pct = rec.get("compatibility_score")
        if score_pct is None:
            match_score = rec.get("match_score")
            score_pct = int(round(match_score * 100)) if match_score is not None else 0

        score_class = "score-high" if score_pct >= 80 else ("score-mid" if score_pct >= 60 else "score-low")
        date_short, date_time = format_history_date(rec.get("timestamp"))

        user_pref = rec.get("user_preferences") or {}
        soil_p = user_pref.get("soil_type") or plant.get("soil_type", "—")
        clim_p = user_pref.get("climate") or plant.get("climate", "—")
        sun_p = user_pref.get("sunlight") or plant.get("sunlight", "—")
        sp_p = user_pref.get("space") or plant.get("space_requirement", "—")

        icon = PLANT_FALLBACK_IMAGES.get(plant_name.lower().strip(), "🌿")

        c1, c2, c3, c4, c5 = st.columns([2, 4, 2, 3, 3])

        with c1:
            render_html(f"""
            <div style="padding-top:0.3rem">
                <strong style="color:#0f3d2e;font-size:0.95rem">{date_short}</strong><br>
                <span style="color:#888;font-size:0.75rem">{date_time}</span>
            </div>
            """)

        with c2:
            render_html(f"""
            <div style="display:flex;align-items:center;gap:0.6rem;padding-top:0.2rem">
                <span style="font-size:1.6rem">{icon}</span>
                <div>
                    <strong style="color:#0f3d2e;font-size:0.98rem">{plant_name}</strong><br>
                    <span style="font-size:0.78rem;color:#64748b;font-style:italic">{sci_name}</span>
                </div>
            </div>
            """)

        with c3:
            render_html(f"""
            <div style="padding-top:0.35rem">
                <span class="score-pill {score_class}">{score_pct}%</span>
            </div>
            """)

        with c4:
            render_html(f"""
            <div style="font-size:0.8rem;color:#475569;padding-top:0.3rem;line-height:1.4">
                🌱 {soil_p}<br>
                ☀️ {sun_p}
            </div>
            """)

        with c5:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🪴 Details", key=f"tbl_btn_plant_{idx}_{rec.get('rec_id', idx)}", use_container_width=True):
                    st.session_state.selected_plant = plant
                    st.session_state.selected_plant_id = plant.get("plant_id")
                    st.session_state.selected_score_data = {
                        "score_pct": score_pct,
                        "score": score_pct,
                        "matched_factors": rec.get("matched_factors", []),
                        "matched": rec.get("matched_factors", []),
                        "unmatched_factors": rec.get("unmatched_factors", []),
                        "unmatched": rec.get("unmatched_factors", []),
                    }
                    st.session_state.page = "🪴 Plant Details"
                    st.rerun()
            with btn_col2:
                with st.popover("👁️ View"):
                    st.markdown(f"### {icon} {plant_name}")
                    st.markdown(f"**Compatibility Score:** `{score_pct}%`")
                    st.markdown(f"**Recommendation Date/Time:** {rec.get('timestamp', '—')}")
                    if rec.get("notes"):
                        st.info(rec["notes"])
                    st.markdown("#### User Preferences Logged")
                    st.markdown(f"- **Soil Type:** {soil_p}")
                    st.markdown(f"- **Climate:** {clim_p}")
                    st.markdown(f"- **Sunlight:** {sun_p}")
                    st.markdown(f"- **Available Space:** {sp_p}")
                    if st.button("🔄 Re-run This Recommendation", key=f"pop_rerun_{idx}", type="primary", use_container_width=True):
                        st.session_state.form_soil = soil_p
                        st.session_state.form_climate = clim_p
                        st.session_state.form_sunlight = sun_p
                        st.session_state.form_space = sp_p
                        st.session_state.trigger_recommendation = True
                        st.session_state.page = "🌱 Recommendations"
                        st.rerun()

        st.markdown("<hr style='margin:0.4rem 0;border:0;border-top:1px solid #f1f5f9'>", unsafe_allow_html=True)


def render_my_history_cards(recommendations: list[dict]):
    """Render previous recommendations in a visual cards layout."""
    if not recommendations:
        render_history_empty_state()
        return

    cols = st.columns(3)
    for idx, rec in enumerate(recommendations):
        plant = rec.get("plant") or {}
        plant_name = plant.get("name") or rec.get("name") or "Unknown Plant"
        sci_name = plant.get("scientific_name") or plant.get("scientificName") or ""
        score_pct = rec.get("compatibility_score")
        if score_pct is None:
            match_score = rec.get("match_score")
            score_pct = int(round(match_score * 100)) if match_score is not None else 0

        score_class = "score-high" if score_pct >= 80 else ("score-mid" if score_pct >= 60 else "score-low")
        date_short, date_time = format_history_date(rec.get("timestamp"))

        user_pref = rec.get("user_preferences") or {}
        soil_p = user_pref.get("soil_type") or plant.get("soil_type", "—")
        clim_p = user_pref.get("climate") or plant.get("climate", "—")
        sun_p = user_pref.get("sunlight") or plant.get("sunlight", "—")
        sp_p = user_pref.get("space") or plant.get("space_requirement", "—")

        icon = PLANT_FALLBACK_IMAGES.get(plant_name.lower().strip(), "🌿")

        with cols[idx % 3]:
            render_html(f"""
            <div class="history-card-box">
                <div>
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem">
                        <span style="font-size:2rem">{icon}</span>
                        <span class="score-pill {score_class}">{score_pct}%</span>
                    </div>
                    <div style="font-weight:700;color:#0f3d2e;font-size:1.05rem;margin-bottom:0.2rem">{plant_name}</div>
                    <div style="font-size:0.8rem;color:#64748b;font-style:italic;margin-bottom:0.6rem">{sci_name}</div>
                    <div style="font-size:0.78rem;color:#888;margin-bottom:0.6rem">📅 {date_short} ({date_time})</div>
                    <div style="font-size:0.82rem;color:#334155;background:#f8fafc;padding:0.5rem 0.7rem;border-radius:8px;margin-bottom:0.8rem">
                        🌱 {soil_p} &nbsp;•&nbsp; ☀️ {sun_p} &nbsp;•&nbsp; 🌡️ {clim_p}
                    </div>
                </div>
            </div>
            """)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🪴 Details", key=f"card_det_{idx}_{rec.get('rec_id', idx)}", use_container_width=True):
                    st.session_state.selected_plant = plant
                    st.session_state.selected_plant_id = plant.get("plant_id")
                    st.session_state.selected_score_data = {
                        "score_pct": score_pct,
                        "score": score_pct,
                        "matched_factors": rec.get("matched_factors", []),
                        "matched": rec.get("matched_factors", []),
                        "unmatched_factors": rec.get("unmatched_factors", []),
                        "unmatched": rec.get("unmatched_factors", []),
                    }
                    st.session_state.page = "🪴 Plant Details"
                    st.rerun()
            with btn_col2:
                with st.popover("👁️ View"):
                    st.markdown(f"### {icon} {plant_name}")
                    st.markdown(f"**Compatibility Score:** `{score_pct}%`")
                    st.markdown(f"**Date:** {rec.get('timestamp', '—')}")
                    if rec.get("notes"):
                        st.info(rec["notes"])
                    st.markdown(f"- **Soil:** {soil_p}\n- **Climate:** {clim_p}\n- **Sunlight:** {sun_p}\n- **Space:** {sp_p}")
                    if st.button("🔄 Re-run Search", key=f"card_rerun_{idx}", type="primary", use_container_width=True):
                        st.session_state.form_soil = soil_p
                        st.session_state.form_climate = clim_p
                        st.session_state.form_sunlight = sun_p
                        st.session_state.form_space = sp_p
                        st.session_state.trigger_recommendation = True
                        st.session_state.page = "🌱 Recommendations"
                        st.rerun()

