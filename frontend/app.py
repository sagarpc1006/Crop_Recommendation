"""Streamlit Frontend Application Entry Point for FloraMatch.

Connects to the Flask REST backend and displays system architecture,
service health, criteria input interface, and catalog preview.
"""

import sys
from pathlib import Path

# Add project root to sys.path so modules resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from frontend.config import APP_TITLE, APP_TAGLINE, BACKEND_API_URL
from frontend.components.ui import inject_custom_css, render_header, render_status_card
from frontend.services.api_client import BackendApiClient

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom visual styling
inject_custom_css()

# API client instance
api_client = BackendApiClient()


def main():
    """Main rendering routine for the Streamlit application."""
    # Top banner header
    render_header(title=APP_TITLE, subtitle=APP_TAGLINE)

    # Sidebar configuration and diagnostics
    with st.sidebar:
        st.header("⚙️ System Status")
        st.caption("Backend & Database Connectivity")

        # Health check call
        health_info = api_client.check_health()
        backend_online = health_info["available"]

        if backend_online:
            db_info = health_info["data"].get("database", {})
            db_connected = db_info.get("connected", False)

            render_status_card(
                title="Flask REST API",
                is_active=True,
                detail=f"Online at {BACKEND_API_URL}"
            )
            render_status_card(
                title="PostgreSQL Database",
                is_active=db_connected,
                detail=db_info.get("message", "Connected" if db_connected else "Offline"),
                is_warning=not db_connected
            )
        else:
            render_status_card(
                title="Flask REST API",
                is_active=False,
                detail=health_info["message"]
            )
            render_status_card(
                title="PostgreSQL Database",
                is_active=False,
                detail="Waiting for backend API..."
            )

        st.divider()
        st.markdown("### 📌 Navigation")
        nav_choice = st.radio(
            "Select Section:",
            ["🌱 Plant Recommendation", "📊 System Architecture", "📚 API & Database Docs"],
            label_visibility="collapsed"
        )

        st.divider()
        st.caption("FloraMatch v1.0.0 • Foundation Architecture")

    # Main area based on navigation
    if nav_choice == "🌱 Plant Recommendation":
        render_recommendation_section(backend_online)
    elif nav_choice == "📊 System Architecture":
        render_architecture_section()
    elif nav_choice == "📚 API & Database Docs":
        render_docs_section()


def render_recommendation_section(backend_online: bool):
    """Render the plant criteria input form and catalog preview."""
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🌾 Specify Growing Conditions")
        st.write("Configure environmental parameters to receive matching plant recommendations:")

        with st.form("criteria_form"):
            soil_type = st.selectbox(
                "Soil Type",
                ["Sandy", "Loamy", "Clay", "Well-drained", "Peaty", "Chalky"],
                index=1,
                help="Select the dominant soil texture in your garden or container."
            )

            climate = st.selectbox(
                "Climate Zone",
                ["Warm/Dry", "Humid/Tropical", "Warm/Tropical", "Warm/Temperate", "Cold/Temperate", "Any/Indoor"],
                index=0,
                help="Your local climate or indoor environmental temperature/humidity."
            )

            sunlight = st.selectbox(
                "Sunlight Availability",
                ["Full Sun", "Partial Shade", "Low Light", "Bright Indirect"],
                index=0,
                help="Amount of daily sunlight exposure available to the plant."
            )

            space_req = st.selectbox(
                "Available Space",
                ["Minimal (Desktop / Pot)", "Compact (Balcony / Window)", "Moderate (Garden Bed)", "Climbing / Hanging", "Expansive (Field)"],
                index=1,
                help="Spatial footprint allocated for plant growth."
            )

            submit_btn = st.form_submit_button("🔍 Find Matching Plants", use_container_width=True)

        if submit_btn:
            st.info(
                f"**Input Criteria Captured:**\n"
                f"- **Soil:** {soil_type}\n"
                f"- **Climate:** {climate}\n"
                f"- **Sunlight:** {sunlight}\n"
                f"- **Space:** {space_req}\n\n"
                "*(Foundation Stage: Recommendation algorithm will execute matching in upcoming stage.)*"
            )

    with col2:
        st.subheader("🌿 Plant Catalog Preview")
        st.write("Sample species seeded in the PostgreSQL database layer:")

        sample_cards = [
            {"name": "Aloe Vera", "soil": "Sandy", "climate": "Warm/Dry", "sun": "Full Sun", "water": "Low", "tag": "Succulent"},
            {"name": "Money Plant", "soil": "Loamy", "climate": "Humid/Tropical", "sun": "Partial Shade", "water": "Medium", "tag": "Indoor Vine"},
            {"name": "Tulsi", "soil": "Loamy", "climate": "Warm/Tropical", "sun": "Full Sun", "water": "Medium", "tag": "Medicinal Herb"},
            {"name": "Snake Plant", "soil": "Well-drained", "climate": "Any/Indoor", "sun": "Low Light", "water": "Low", "tag": "Hardy / Purifier"},
            {"name": "Marigold", "soil": "Loamy", "climate": "Warm/Temperate", "sun": "Full Sun", "water": "Medium", "tag": "Flowering Annual"},
        ]

        for plant in sample_cards:
            with st.container(border=True):
                c_title, c_tag = st.columns([3, 1])
                c_title.markdown(f"**{plant['name']}**")
                c_tag.caption(f"`{plant['tag']}`")
                st.caption(
                    f"Soil: **{plant['soil']}** • Climate: **{plant['climate']}** • "
                    f"Sunlight: **{plant['sun']}** • Water: **{plant['water']}**"
                )


def render_architecture_section():
    """Render details regarding the system structure and layers."""
    st.subheader("🏛️ Production-Style Layered Architecture")
    st.markdown("""
    The application is architected into decoupled, modular tiers:

    ```
    ┌─────────────────────────┐
    │   Streamlit Frontend    │  UI Presentation & State Management (Port 8501)
    └────────────┬────────────┘
                 │ HTTP / REST
                 ▼
    ┌─────────────────────────┐
    │     Flask REST API      │  Routing, CORS, Serialization, API Factory (Port 5000)
    └────────────┬────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
┌─────────────┐       ┌─────────────┐
│ Services &  │       │ PostgreSQL  │  SQLAlchemy 2.0+ Declarative ORM
│ Recommender │       │ Database    │  Alembic Migrations & Connection Pooling
└─────────────┘       └─────────────┘
    ```
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        #### Layer Responsibilities
        - **Frontend (`frontend/`)**: Modern Streamlit interface with styled components and isolated HTTP client.
        - **Backend REST API (`backend/api/`)**: Blueprint routes delivering JSON payloads with standard response envelopes.
        - **Database Layer (`backend/database/`)**: Declarative models (`User`, `Plant`, `Recommendation`, `SearchHistory`), connection pool management, and Alembic migrations.
        """)
    with col_b:
        st.markdown("""
        #### Modularity Highlights
        - **Service Layer (`backend/services/`)**: Business logic isolated from Flask view functions.
        - **Recommendation Engine (`backend/recommendation/`)**: Decoupled interface for future heuristic or ML algorithms.
        - **External Integrations (`backend/integrations/`)**: Scaffolded clients for Perenual and Trefle botanical APIs.
        """)


def render_docs_section():
    """Render database schema and API documentation."""
    st.subheader("📚 Database Schema & REST Endpoints")

    tab1, tab2 = st.tabs(["🗄️ Relational Schema", "🌐 REST API Endpoints"])

    with tab1:
        st.markdown("""
        #### Core Tables
        1. **`users`**:
           - `user_id` (PK), `name`, `email` (Unique), `location`, `created_at`, `updated_at`
        2. **`plants`**:
           - `plant_id` (PK), `name` (Unique), `soil_type`, `climate`, `sunlight`, `water_needs`, `space_requirement`, `description`
        3. **`recommendations`**:
           - `rec_id` (PK), `user_id` (FK), `plant_id` (FK), `search_id` (FK), `match_score`, `timestamp`
        4. **`search_history`**:
           - `history_id` (PK), `user_id` (FK), criteria fields, `results_count`, `timestamp`
        """)

    with tab2:
        st.markdown("""
        #### Foundation REST Endpoints
        - `GET /api/v1/health`: Connectivity report for Flask API and PostgreSQL.
        - `GET /api/v1/info`: Metadata regarding system capabilities and supported criteria.
        - `GET /api/v1/plants`: Plant catalog retrieval (paginated).
        - `POST /api/v1/recommendations`: Recommender endpoint accepting environmental criteria.
        """)


if __name__ == "__main__":
    main()
