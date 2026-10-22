"""GROWIT – Plant Recommendation Website — Streamlit Frontend Application.

7 sections:
  1. Home          — Hero, features, CTA
  2. Recommendations — Criteria form + live results from Flask API
  3. Plant Search  — Full-text search against local DB + Perenual API
  4. Plant Details — Enriched single-plant view
  5. History       — Session-based search history
  6. Care Guide    — Static plant-care knowledge base
  7. About         — Architecture & API docs (kept from foundation)

All data comes from the Flask REST backend — no hardcoded/fake records.
"""

import sys
import datetime
from pathlib import Path

# ── Path bootstrap ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Streamlit ──────────────────────────────────────────────────────────────────
import streamlit as st

# ── Local modules ──────────────────────────────────────────────────────────────
from frontend.config import APP_TITLE, BACKEND_API_URL
from frontend.services.api_client import BackendApiClient
from frontend.components.ui import (
    inject_custom_css,
    render_hero,
    render_header,
    render_status_card,
    render_plant_card,
    render_plant_detail,
    render_search_row,
    render_care_guide,
    render_feature_cards,
    render_history,
    render_my_history_table,
    render_my_history_cards,
    render_history_empty_state,
    render_empty_state,
    render_error_state,
    section_heading,
    SOIL_ICONS, SUNLIGHT_ICONS, CLIMATE_ICONS,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GROWIT – Plant Recommendation Website",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "GROWIT v1.0 – Plant Recommendation Website. Smart plant recommendations for every environment."},
)
inject_custom_css()

# ── API Client (cached at module level) ────────────────────────────────────────
@st.cache_resource
def get_api_client() -> BackendApiClient:
    return BackendApiClient()

api = get_api_client()

# ── Session state initialisation ───────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "selected_plant" not in st.session_state:
    st.session_state.selected_plant = None
if "selected_score_data" not in st.session_state:
    st.session_state.selected_score_data = None
if "last_rec_results" not in st.session_state:
    st.session_state.last_rec_results = []
if "last_rec_criteria" not in st.session_state:
    st.session_state.last_rec_criteria = {}
if "rec_error" not in st.session_state:
    st.session_state.rec_error = None
if "rec_empty" not in st.session_state:
    st.session_state.rec_empty = False
if "trigger_recommendation" not in st.session_state:
    st.session_state.trigger_recommendation = False
if "form_soil" not in st.session_state:
    st.session_state.form_soil = "Loamy"
if "form_climate" not in st.session_state:
    st.session_state.form_climate = "Tropical"
if "form_sunlight" not in st.session_state:
    st.session_state.form_sunlight = "Partial Shade"
if "form_space" not in st.session_state:
    st.session_state.form_space = "Small"
if "form_limit" not in st.session_state:
    st.session_state.form_limit = 5
if "form_enrich" not in st.session_state:
    st.session_state.form_enrich = False
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = "Botanical Explorer"
if "user_email" not in st.session_state:
    st.session_state.user_email = "explorer@example.com"
if "user_location" not in st.session_state:
    st.session_state.user_location = "Austin, TX"
if "history_view_mode" not in st.session_state:
    st.session_state.history_view_mode = "Table"

# Normalize legacy page name if needed
if st.session_state.page in ("🕒 History", "My History"):
    st.session_state.page = "📜 My History"


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

NAV_PAGES = [
    "🏠 Home",
    "🌱 Recommendations",
    "🔍 Plant Search",
    "🪴 Plant Details",
    "📜 My History",
    "📖 Care Guide",
    "⚙️ About",
]

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
        <span style="font-size:2.5rem">🌿</span>
        <div style="font-weight:800;font-size:1.15rem;color:#e8f5e9;margin-top:0.3rem">GROWIT</div>
        <div style="font-size:0.75rem;color:#81c784">Plant Recommendation Website</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # User profile section
    st.markdown('<div style="color:#a5d6a7;font-size:0.8rem;font-weight:600;letter-spacing:0.5px;margin-bottom:0.4rem">USER PROFILE</div>',
                unsafe_allow_html=True)
    with st.expander(f"👤 {st.session_state.user_name}", expanded=False):
        new_name = st.text_input("Name", value=st.session_state.user_name, key="profile_name_input")
        new_email = st.text_input("Email", value=st.session_state.user_email, key="profile_email_input",
                                  placeholder="your@email.com")
        new_location = st.text_input("Location", value=st.session_state.user_location, key="profile_loc_input",
                                     placeholder="e.g. Mumbai, India")
        if st.button("💾 Save Profile", key="btn_save_profile", use_container_width=True):
            st.session_state.user_name = new_name.strip() or "Botanical Explorer"
            st.session_state.user_email = new_email.strip() or "explorer@example.com"
            st.session_state.user_location = new_location.strip()
            st.success("Profile saved!")
            st.rerun()

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08);border-radius:8px;padding:0.5rem 0.8rem;margin-bottom:0.8rem">
        <div style="font-weight:700;color:#e8f5e9;font-size:0.88rem">👤 {st.session_state.user_name}</div>
        <div style="font-size:0.75rem;color:#a5d6a7">User ID: #{st.session_state.current_user_id} {('· ' + st.session_state.user_location) if st.session_state.user_location else ''}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="color:#a5d6a7;font-size:0.8rem;font-weight:600;letter-spacing:0.5px;margin-bottom:0.5rem">NAVIGATION</div>',
                unsafe_allow_html=True)
    nav_index = NAV_PAGES.index(st.session_state.page) if st.session_state.page in NAV_PAGES else 0
    page = st.radio("page", NAV_PAGES, label_visibility="collapsed", index=nav_index)
    st.session_state.page = page
    st.divider()

    # System status
    st.markdown('<div style="color:#a5d6a7;font-size:0.8rem;font-weight:600;letter-spacing:0.5px;margin-bottom:0.5rem">SYSTEM STATUS</div>',
                unsafe_allow_html=True)
    health = api.check_health()
    backend_online = health["available"]
    db_info = health["data"].get("database", {}) if backend_online else {}
    db_connected = db_info.get("connected", False)
    ext_api_info = health["data"].get("external_plant_api", {}) if backend_online else {}
    ext_configured = ext_api_info.get("provider_configured", False)

    render_status_card("Flask API", backend_online,
                       BACKEND_API_URL if backend_online else health["message"])
    render_status_card("PostgreSQL", db_connected,
                       db_info.get("message", "Not connected"),
                       is_warning=backend_online and not db_connected)
    render_status_card("Plant API", ext_configured,
                       f"Cache: {ext_api_info.get('cache_entries', 0)} entries"
                       if ext_configured else "Set PLANT_API_KEY to enable",
                       is_warning=not ext_configured)

    if not backend_online:
        st.warning("Flask server offline. Start it with:\n`python -m flask run`")

    st.divider()
    history_count = len(st.session_state.search_history)
    st.markdown(f'<div style="color:#81c784;font-size:0.8rem;text-align:center">🕒 {history_count} search{"es" if history_count != 1 else ""} this session</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════

def page_home():
    cta_clicked = render_hero(show_cta=True)
    if cta_clicked:
        st.session_state.page = "🌱 Recommendations"
        st.rerun()

    section_heading("✨", "Why GROWIT?")
    render_feature_cards()

    st.markdown("")
    section_heading("🌿", "Featured Plants")

    plants = api.get_plants(limit=5)
    if not plants:
        st.info("Start the Flask backend to see the live plant catalog here.")
        return

    cols = st.columns(min(len(plants), 5))
    for col, plant in zip(cols, plants):
        with col:
            emoji = {"aloe vera": "🌵", "money plant": "🍀", "tulsi": "🌿",
                     "snake plant": "🌱", "marigold": "🌼"}.get(
                plant.get("name", "").lower(), "🌿")
            st.markdown(f"""
            <div class="feature-card" style="cursor:pointer">
                <div class="icon">{emoji}</div>
                <h3 style="font-size:0.9rem">{plant.get('name','')}</h3>
                <p>{plant.get('climate','—')} · {plant.get('sunlight','—')}</p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

SOIL_OPTIONS    = ["Sandy", "Loamy", "Clay", "Well-drained", "Peaty", "Chalky"]
CLIMATE_OPTIONS = ["Warm/Dry", "Humid/Tropical", "Warm/Tropical",
                   "Warm/Temperate", "Cold/Temperate", "Any/Indoor"]
SUNLIGHT_OPTIONS = ["Full Sun", "Partial Shade", "Low Light", "Bright Indirect"]
SPACE_OPTIONS   = ["Small", "Medium", "Large", "Minimal", "Expansive"]


def page_recommendations():
    render_header("Plant Recommendations",
                  "Find the Right Plant for Your Space")

    # Safe option indices based on session state
    soil_idx = SOIL_OPTIONS.index(st.session_state.form_soil) if st.session_state.form_soil in SOIL_OPTIONS else 1
    climate_idx = CLIMATE_OPTIONS.index(st.session_state.form_climate) if st.session_state.form_climate in CLIMATE_OPTIONS else 0
    sunlight_idx = SUNLIGHT_OPTIONS.index(st.session_state.form_sunlight) if st.session_state.form_sunlight in SUNLIGHT_OPTIONS else 0
    space_idx = SPACE_OPTIONS.index(st.session_state.form_space) if st.session_state.form_space in SPACE_OPTIONS else 0

    form_col, gap, result_col = st.columns([1, 0.05, 1.6])

    with form_col:
        section_heading("🌾", "Find the Right Plant for Your Space")
        st.markdown('<p style="color:#555;font-size:0.9rem;margin-bottom:1rem">Configure your environmental conditions to receive personalized plant matches.</p>',
                    unsafe_allow_html=True)

        with st.form("recommendation_form", clear_on_submit=False):
            soil = st.selectbox(
                f"{SOIL_ICONS.get('Sandy','🌍')} Soil Type",
                SOIL_OPTIONS, index=soil_idx,
                help="The primary soil texture in your garden or container."
            )
            climate = st.selectbox(
                f"{CLIMATE_ICONS.get('Warm/Dry','🌡️')} Climate Zone",
                CLIMATE_OPTIONS, index=climate_idx,
                help="Your local climate or indoor temperature/humidity."
            )
            sunlight = st.selectbox(
                f"{SUNLIGHT_ICONS.get('Full Sun','☀️')} Sunlight Availability",
                SUNLIGHT_OPTIONS, index=sunlight_idx,
                help="Daily sunlight hours your planting spot receives."
            )
            space = st.selectbox(
                "📐 Available Space",
                SPACE_OPTIONS, index=space_idx,
                help="How much space you can dedicate to plant growth."
            )
            n_results = st.slider(
                "Number of recommendations", 1, 10,
                value=int(st.session_state.form_limit)
            )
            enrich = st.checkbox(
                "🌐 Enrich with external images & care data",
                value=bool(st.session_state.form_enrich),
                help="Pulls extra data from Perenual API. Requires PLANT_API_KEY."
            )

            submitted = st.form_submit_button(
                "🌱 Get Recommendations", type="primary", use_container_width=True
            )

        # Handle form submission or programmatic trigger (retry)
        should_run = submitted or st.session_state.trigger_recommendation
        if should_run:
            st.session_state.trigger_recommendation = False
            # Persist selected criteria in session state so inputs stay sticky
            st.session_state.form_soil = soil
            st.session_state.form_climate = climate
            st.session_state.form_sunlight = sunlight
            st.session_state.form_space = space
            st.session_state.form_limit = n_results
            st.session_state.form_enrich = enrich

            st.session_state.rec_error = None
            st.session_state.rec_empty = False

            with st.spinner("🌿 Analyzing soil, climate, sunlight, and space compatibility with Flask recommendation engine…"):
                rec_result = api.generate_recommendations(
                    soil_type=soil,
                    climate=climate,
                    sunlight=sunlight,
                    space=space,
                    limit=n_results,
                    enrich=enrich,
                    user_id=st.session_state.get("current_user_id", 1),
                    user_name=st.session_state.get("user_name"),
                    user_email=st.session_state.get("user_email"),
                    user_location=st.session_state.get("user_location"),
                )

                if rec_result["ok"]:
                    recs = rec_result.get("recommendations", [])
                    st.session_state.last_rec_criteria = {
                        "soil_type": soil, "climate": climate,
                        "sunlight": sunlight, "space": space,
                    }
                    if recs:
                        st.session_state.last_rec_results = recs
                        st.session_state.rec_error = None
                        st.session_state.rec_empty = False
                        # Save to session history
                        st.session_state.search_history.append({
                            "criteria": st.session_state.last_rec_criteria,
                            "results":  recs,
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        })
                    else:
                        st.session_state.last_rec_results = []
                        st.session_state.rec_error = None
                        st.session_state.rec_empty = True
                else:
                    st.session_state.last_rec_results = []
                    st.session_state.rec_empty = False
                    st.session_state.rec_error = {
                        "error_type": rec_result.get("error_type", "unknown"),
                        "message": rec_result.get("message", "Recommendation request failed."),
                    }

    with result_col:
        # 1. Error State (Backend Unavailable, Timeout, or HTTP Error)
        if st.session_state.rec_error:
            err = st.session_state.rec_error
            render_error_state(err.get("error_type", "unknown"), err.get("message", ""))
            if st.button("🔄 Retry Recommendation", key="btn_retry_error", type="primary", use_container_width=True):
                st.session_state.trigger_recommendation = True
                st.rerun()

        # 2. Empty Result State (No plants matched criteria)
        elif st.session_state.rec_empty:
            render_empty_state(st.session_state.last_rec_criteria)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔄 Broaden Criteria & Retry", key="btn_broaden_retry", type="primary", use_container_width=True):
                    st.session_state.form_climate = "Warm/Tropical"
                    st.session_state.form_sunlight = "Partial Shade"
                    st.session_state.trigger_recommendation = True
                    st.rerun()
            with col_b2:
                if st.button("🔁 Retry Same Query", key="btn_retry_same", use_container_width=True):
                    st.session_state.trigger_recommendation = True
                    st.rerun()

        # 3. Top Recommendations Display
        elif st.session_state.last_rec_results:
            recs = st.session_state.last_rec_results
            crit = st.session_state.last_rec_criteria
            soil_tag = crit.get("soil_type", "Selected")
            sun_tag  = crit.get("sunlight", "Sunlight")
            clim_tag = crit.get("climate", "Climate")

            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.8rem">
                <div>
                    <h3 style="color:#0f3d2e;margin:0;font-size:1.15rem">🎯 Best Plant Matches ({len(recs)})</h3>
                    <span style="font-size:0.82rem;color:#666">
                        Matched for: <strong>{soil_tag}</strong> soil · <strong>{sun_tag}</strong> · <strong>{clim_tag}</strong>
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(2, gap="medium")
            for i, rec in enumerate(recs):
                plant      = rec.get("plant", rec)  # handles both flat and nested structures
                score_raw  = rec.get("compatibility_score", rec.get("score", 0))
                score_pct  = round(score_raw * 100 if score_raw <= 1 else score_raw)
                matched    = rec.get("matched_factors", [])
                unmatched  = rec.get("unmatched_factors", [])

                with cols[i % 2]:
                    render_plant_card(
                        plant=plant,
                        score=score_pct,
                        matched=matched,
                        unmatched=unmatched,
                    )
                    if st.button("🔍 View Details", key=f"rec_details_{i}_{plant.get('plant_id', i)}"):
                        st.session_state.selected_plant = plant
                        st.session_state.selected_plant_id = plant.get("plant_id") or plant.get("id")
                        st.session_state.selected_score_data = {
                            "score_pct": score_pct,
                            "matched_factors": matched,
                            "unmatched_factors": unmatched,
                        }
                        st.session_state.page = "🪴 Plant Details"
                        st.rerun()

        # 4. Initial Landing Placeholder
        else:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;color:#888">
                <div style="font-size:4rem;margin-bottom:1rem">🌱</div>
                <strong style="font-size:1.15rem;color:#0f3d2e">Configure & Recommend</strong><br>
                <span style="font-size:0.9rem">Select your soil type, climate, sunlight, and available space on the left.<br>
                Click <em>🌱 Recommend Plants</em> to compute transparent compatibility scores.</span>
            </div>
            """, unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PLANT SEARCH
# ══════════════════════════════════════════════════════════════════════════════

def page_search():
    render_header(
        "Plant Search & Botanical Catalog",
        "Search across our botanical collection by plant name, soil type, climate, or sunlight conditions."
    )

    # Search Form with explicit [ 🔍 Search ] button
    with st.form("plant_search_form", clear_on_submit=False):
        col_q, col_src, col_btn = st.columns([3.5, 1.5, 1])
        with col_q:
            query = st.text_input(
                "Search plants",
                value=st.session_state.get("search_query", ""),
                placeholder="Search by name, soil, climate, or sunlight… (e.g. Aloe, Sandy, Tropical, Full Sun)",
                help="Enter any plant name, preferred soil, climate zone, or sunlight requirement."
            )
        with col_src:
            source = st.selectbox(
                "Data Source",
                ["All Sources", "Local Database", "External API"],
                index=0,
                help="Choose whether to search local catalog or query live external botanical index."
            )
            src_map = {"All Sources": "all", "Local Database": "local", "External API": "external"}
        with col_btn:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            search_submitted = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)

    if search_submitted:
        st.session_state.search_query = query.strip()

    # Quick discovery filter chips
    st.markdown(
        '<div style="display:flex;align-items:center;gap:0.4rem;margin:0.2rem 0 1rem 0;flex-wrap:wrap">'
        '<span style="font-size:0.8rem;font-weight:700;color:#555">QUICK FILTERS:</span>'
        '</div>',
        unsafe_allow_html=True
    )
    filter_chips = [
        ("🌿 Aloe Vera", "Aloe Vera"),
        ("🌸 Tulsi", "Tulsi"),
        ("☀️ Full Sun", "Full Sun"),
        ("⛅ Partial Shade", "Partial Shade"),
        ("🏜️ Sandy Soil", "Sandy"),
        ("🌍 Loamy Soil", "Loamy"),
        ("🌴 Tropical", "Tropical"),
    ]
    chip_cols = st.columns(len(filter_chips))
    for col, (label, val) in zip(chip_cols, filter_chips):
        with col:
            if st.button(label, key=f"filter_{val}", use_container_width=True):
                st.session_state.search_query = val
                st.rerun()

    active_query = st.session_state.get("search_query", "").strip()

    def _open_details(selected_plant: dict):
        st.session_state.selected_plant = selected_plant
        st.session_state.selected_plant_id = selected_plant.get("plant_id") or selected_plant.get("id")
        st.session_state.selected_score_data = None
        st.session_state.page = "🪴 Plant Details"
        st.rerun()

    if active_query:
        with st.spinner(f"🔍 Searching plants for '{active_query}'…"):
            results = api.search_plants(active_query, source=src_map.get(source, "all"))

        col_head, col_clear = st.columns([4, 1])
        with col_head:
            n_res = len(results)
            section_heading("🌿", f"{n_res} Plant{'s' if n_res != 1 else ''} Found for '{active_query}'")
        with col_clear:
            if st.button("✕ Clear Search", key="btn_clear_search"):
                st.session_state.search_query = ""
                st.rerun()

        if results:
            # Display results as plant cards in a responsive grid
            card_cols = st.columns(2, gap="medium")
            for idx, plant in enumerate(results):
                with card_cols[idx % 2]:
                    render_plant_card(
                        plant=plant,
                        show_score=False,
                        on_details=_open_details,
                        key_suffix=f"search_{idx}_{plant.get('plant_id', idx)}"
                    )
        else:
            st.markdown(f"""
            <div style="text-align:center;padding:2.5rem;background:white;border-radius:14px;border:1px dashed #cbd5e1;margin:1rem 0">
                <div style="font-size:3rem;margin-bottom:0.5rem">🔍</div>
                <h3 style="color:#0f3d2e;margin:0 0 0.4rem 0">No plants matched '{active_query}'</h3>
                <p style="color:#64748b;font-size:0.9rem;margin:0 0 1rem 0">
                    Try searching by <strong>soil type</strong> (e.g. Sandy, Loamy),
                    <strong>climate</strong> (e.g. Tropical, Warm/Dry), or
                    <strong>sunlight</strong> (e.g. Full Sun, Low Light).
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Full catalog view when no query is typed
        section_heading("📚", "Full Botanical Catalog")
        st.markdown("<p style='color:#666;font-size:0.88rem;margin-bottom:1rem'>Browse all curated species in the local botanical database or search above.</p>", unsafe_allow_html=True)

        catalog_plants = api.get_plants(limit=50)
        if catalog_plants:
            card_cols = st.columns(2, gap="medium")
            for idx, plant in enumerate(catalog_plants):
                with card_cols[idx % 2]:
                    render_plant_card(
                        plant=plant,
                        show_score=False,
                        on_details=_open_details,
                        key_suffix=f"catalog_{idx}_{plant.get('plant_id', idx)}"
                    )
        else:
            st.info("No plants currently loaded in database. Seed sample data or ensure Flask server is running.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PLANT DETAILS
# ══════════════════════════════════════════════════════════════════════════════

def page_details():
    col_nav1, col_nav2 = st.columns([1, 4])
    with col_nav1:
        if st.button("← Back to Search", use_container_width=True):
            st.session_state.page = "🔍 Plant Search"
            st.rerun()

    plant = st.session_state.get("selected_plant")
    plant_id = st.session_state.get("selected_plant_id") or (plant.get("plant_id") if plant else None) or (plant.get("id") if plant else None)

    if not plant and not plant_id:
        st.info("No plant selected. Use Search or Recommendations to select a plant to view.")
        if st.button("Go to Plant Search", type="primary"):
            st.session_state.page = "🔍 Plant Search"
            st.rerun()
        return

    # Fetch combined local + external API plant record via GET /api/plants/<plant_id>
    detailed_plant = plant or {}
    if plant_id:
        with st.spinner("Fetching full botanical profile with live external enrichment…"):
            fresh = api.get_plant_details(int(plant_id), enrich=True)
            if fresh:
                detailed_plant = fresh
                st.session_state.selected_plant = fresh

    with st.container():
        render_plant_detail(
            plant=detailed_plant,
            score_data=st.session_state.get("selected_score_data"),
        )

    # Action footer
    st.markdown("<hr style='margin:2rem 0 1.5rem 0;border:0;border-top:1px solid #e8f5e9'>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2, gap="medium")
    with col_btn1:
        if st.button("🌱 Recommend Similar Plants", type="primary", use_container_width=True):
            care = detailed_plant.get("basic_care") or {}
            st.session_state.form_soil = detailed_plant.get("soil_type") or care.get("soil_type") or "Loamy"
            st.session_state.form_climate = detailed_plant.get("climate") or care.get("climate") or "Warm/Dry"
            st.session_state.form_sunlight = detailed_plant.get("sunlight") or care.get("sunlight") or "Full Sun"
            st.session_state.form_space = detailed_plant.get("space_requirement") or care.get("space_requirement") or "Small"
            st.session_state.trigger_recommendation = True
            st.session_state.page = "🌱 Recommendations"
            st.rerun()
    with col_btn2:
        if st.button("🔍 Search More Plants", use_container_width=True):
            st.session_state.page = "🔍 Plant Search"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY ("My History")
# ══════════════════════════════════════════════════════════════════════════════

def page_history():
    render_header("My History", "Review your saved botanical recommendations, compatibility scores, and preferences.")

    # Top Toolbar: View mode selector & User filter
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 2, 1])
    with col_ctrl1:
        view_mode = st.radio(
            "View Mode:",
            ["📊 Table View", "🎴 Cards View"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.get("history_view_mode", "Table") == "Table" else 1,
        )
        st.session_state.history_view_mode = "Table" if "Table" in view_mode else "Cards"

    with col_ctrl2:
        u_id = st.number_input(
            "Filter User ID:",
            min_value=1,
            max_value=9999,
            value=int(st.session_state.get("current_user_id", 1)),
            step=1,
            help="Filter recommendation records saved for this user.",
            label_visibility="collapsed",
        )
        if int(u_id) != st.session_state.get("current_user_id", 1):
            st.session_state.current_user_id = int(u_id)
            st.rerun()

    with col_ctrl3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    tab_my_history, tab_session = st.tabs([
        "🌿 My Recommendations (PostgreSQL)",
        "🕒 Browser Session Searches"
    ])

    with tab_my_history:
        if not backend_online:
            st.error("Backend API is currently offline. Please launch the Flask backend server to view database history.")
        else:
            with st.spinner("Loading recommendation history from PostgreSQL…"):
                user_id = st.session_state.get("current_user_id", 1)
                recs = api.get_user_recommendations(user_id=user_id, limit=50)

            if not recs:
                render_history_empty_state()
            else:
                if st.session_state.history_view_mode == "Table":
                    render_my_history_table(recs)
                else:
                    render_my_history_cards(recs)

    with tab_session:
        col_hist, col_clear = st.columns([4, 1])
        with col_clear:
            if st.button("🗑️ Clear Session") and st.session_state.search_history:
                st.session_state.search_history = []
                st.rerun()

        section_heading("🕒", "Search Sessions This Session")
        rerun_criteria = render_history(st.session_state.search_history)
        if rerun_criteria:
            st.session_state.form_soil = rerun_criteria.get("soil_type", "Loamy")
            st.session_state.form_climate = rerun_criteria.get("climate", "Tropical")
            st.session_state.form_sunlight = rerun_criteria.get("sunlight", "Partial Shade")
            st.session_state.form_space = rerun_criteria.get("space", "Small")
            st.session_state.trigger_recommendation = True
            st.session_state.page = "🌱 Recommendations"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CARE GUIDE
# ══════════════════════════════════════════════════════════════════════════════

def page_care_guide():
    render_header("Plant Care Guide", "Essential knowledge for growing healthy, thriving plants.")
    render_care_guide()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT / ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════

def page_about():
    render_header("About GROWIT", "Architecture, API documentation, and project information.")

    tab_arch, tab_api, tab_db = st.tabs([
        "🏛️ Architecture", "🌐 REST API", "🗄️ Database Schema"
    ])

    with tab_arch:
        section_heading("🏛️", "Layered Architecture")
        st.code("""
┌─────────────────────────────────────────────┐
│         Streamlit Frontend  (Port 8501)      │
│   Pages: Home · Recs · Search · Details     │
│         History · Care Guide                 │
└──────────────────┬──────────────────────────┘
                   │  HTTP / REST JSON
                   ▼
┌─────────────────────────────────────────────┐
│         Flask REST API  (Port 5000)          │
│  /api/plants  /api/recommendations/generate  │
│  /api/plants/search   /api/plants/{id}/enrich│
└──────────┬────────────────────┬─────────────┘
           │                    │
           ▼                    ▼
┌─────────────────┐    ┌──────────────────────┐
│  PlantApiService │    │    PostgreSQL DB      │
│  (Perenual API) │    │  SQLAlchemy 2.0 ORM  │
│  TTL Cache      │    │  Alembic Migrations  │
└─────────────────┘    └──────────────────────┘
        """, language="text")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
**Frontend (`frontend/`)**
- `app.py` — 7-page Streamlit app
- `components/ui.py` — Design system & cards
- `services/api_client.py` — HTTP client

**Backend API (`backend/api/`)**
- Blueprint routes with JSON envelopes
- CORS configured for Streamlit origin
- Pagination, validation, error handling
            """)
        with col_b:
            st.markdown("""
**Database (`backend/database/`)**
- `models/` — User, Plant, Recommendation, SearchHistory
- `manage.py` — CLI for init/seed/migrate

**Recommendation Engine (`backend/recommendation/`)**
- Weighted scoring across 4 criteria
- Fully explainable: matched/unmatched factors

**External Integrations (`backend/integrations/`)**
- `perenual_client.py` — HTTP client with fallback
- `schema.py` — Normalized plant schema
            """)

    with tab_api:
        section_heading("🌐", "REST Endpoints")
        endpoints = [
            ("GET",  "/api/health",                    "Backend & DB connectivity report"),
            ("GET",  "/api/info",                      "System capabilities & metadata"),
            ("GET",  "/api/plants",                    "Paginated plant catalog (limit, offset)"),
            ("GET",  "/api/plants/{id}",               "Single plant by ID"),
            ("GET",  "/api/plants/search?q=<query>",   "Multi-source plant search"),
            ("GET",  "/api/plants/{id}/enrich",        "Plant + external API enrichment"),
            ("POST", "/api/recommendations/generate",  "Score-based recommendations"),
        ]
        for method, path, desc in endpoints:
            color = "#1a5c40" if method == "GET" else "#7c3aed"
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:0.8rem 1rem;
                        margin-bottom:0.6rem;border:1px solid #e8f5e9">
                <span style="background:{color};color:white;border-radius:5px;
                             padding:0.2rem 0.6rem;font-size:0.78rem;font-weight:700">{method}</span>
                &nbsp;<code style="color:#0f3d2e;font-size:0.9rem">{path}</code>
                <span style="color:#666;font-size:0.85rem;margin-left:1rem">— {desc}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Example — Generate Recommendations:**")
        st.code("""{
  "soil_type": "Loamy",
  "climate": "Warm/Tropical",
  "sunlight": "Full Sun",
  "space": "Small",
  "limit": 5,
  "enrich": true
}""", language="json")

    with tab_db:
        section_heading("🗄️", "Relational Schema")
        st.markdown("""
| Table | Primary Key | Key Columns |
|-------|-------------|-------------|
| `users` | `user_id` | `name`, `email` (unique), `location`, `created_at` |
| `plants` | `plant_id` | `name` (unique), `soil_type`, `climate`, `sunlight`, `water_needs`, `space_requirement` |
| `recommendations` | `rec_id` | `user_id` (FK), `plant_id` (FK), `match_score`, `timestamp` |
| `search_history` | `history_id` | `user_id` (FK), criteria fields, `results_count`, `timestamp` |
        """)
        st.markdown("""
**Indexes:**  `plants.name`, `plants.soil_type`, `plants.climate`, `plants.sunlight`,
`recommendations.user_id`, `search_history.user_id`
        """)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    p = st.session_state.page
    if p == "🏠 Home":
        page_home()
    elif p == "🌱 Recommendations":
        page_recommendations()
    elif p == "🔍 Plant Search":
        page_search()
    elif p == "🪴 Plant Details":
        page_details()
    elif p in ("📜 My History", "🕒 History", "My History"):
        page_history()
    elif p == "📖 Care Guide":
        page_care_guide()
    elif p == "⚙️ About":
        page_about()


if __name__ == "__main__":
    main()
