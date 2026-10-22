# GROWIT – Plant Recommendation Website

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/backend-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit%201.35-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-orange.svg)](https://www.sqlalchemy.org/)

## 📌 Project Title

**GROWIT – Plant Recommendation Website**

## 📖 Project Description

GROWIT is a smart web application that recommends suitable plants based on environmental growing conditions. Users provide their soil type, climate, sunlight availability, and available space, and the system recommends the most compatible plants using a content-based recommendation approach with transparent, explainable scoring.

## ❓ Problem Statement

Selecting the right plant for a specific environment is challenging for home gardeners, students, and urban farmers. Factors such as soil composition, local climate, available sunlight, and spatial constraints must be carefully considered. GROWIT addresses this problem by providing personalized, data-driven plant recommendations that match plants to the user's specific growing conditions.

## 🎯 Objectives

1. Develop a web-based plant recommendation system using Streamlit and Flask.
2. Implement a content-based recommendation engine evaluating soil, climate, sunlight, and space compatibility.
3. Store and manage plant data using PostgreSQL with SQLAlchemy ORM.
4. Integrate external botanical APIs (Perenual) for enriched plant information.
5. Provide an intuitive, user-friendly interface for plant discovery and care guidance.

## ✨ Features

- **Plant Recommendation** — Content-based recommendations using weighted scoring across 4 environmental factors
- **Plant Search** — Full-text search across plant name, soil type, climate, and sunlight
- **Plant Details** — Comprehensive plant profiles with care instructions and growing requirements
- **User History** — Persistent recommendation history stored in PostgreSQL
- **Care Guide** — Built-in plant care knowledge base covering watering, light, soil, and fertilizing
- **External API Enrichment** — Live plant images and care data from Perenual botanical API
- **User Profile** — Lightweight user profile with name, email, and location
- **About Section** — Architecture documentation, API reference, and database schema

## 🏛️ System Architecture

```text
User
 ↓
Streamlit Frontend (Port 8501)
 ↓  HTTP REST requests (JSON)
Flask REST API (Port 5000)
 ↓  Criteria evaluation & scoring
Recommendation Engine (Content-Based Weighted Scoring)
 ↓  Candidate query & persistent history
PostgreSQL Database (Users, Plants, Recommendations, Search History)
 ↓  External enrichment (cached with fallback)
External Botanical API (Perenual API)
```

### Component Responsibilities

| Component | Technology | Primary Role |
| :--- | :--- | :--- |
| **Streamlit Frontend** | Streamlit, Requests, Custom CSS | Interactive UI, recommendation form, plant search, plant details, history, care guide, about |
| **Flask REST API** | Flask 3.0, Flask-CORS, Gunicorn | REST endpoints under `/api`, validation, error handling, JSON response envelopes |
| **Recommendation Engine** | Python Dataclasses | Deterministic scoring: Climate (30%), Sunlight (30%), Soil (20%), Space (20%) with explainability |
| **PostgreSQL Database** | PostgreSQL, SQLAlchemy 2.0, Alembic | Persistent storage of plants, users, recommendations, and search history |
| **External Botanical API** | Perenual API, In-Process TTL Cache | Supplements local catalog with images and care data; graceful offline fallback |

## 🧰 Technology Stack

- **Frontend:** Streamlit 1.35+
- **Backend:** Flask 3.0, Flask-CORS
- **Database:** PostgreSQL 14+, SQLAlchemy 2.0, Alembic
- **External API:** Perenual Plant API
- **Testing:** pytest 8.0+
- **Deployment:** Gunicorn, Render, Railway

## 🧪 Recommendation Methodology

GROWIT uses a **content-based recommendation system** with deterministic weighted scoring:

| Factor | Weight | Description |
| :--- | :--- | :--- |
| Climate | 30% | Evaluates compatibility between user's climate zone and plant's preferred climate |
| Sunlight | 30% | Matches user's available sunlight with plant's light requirements |
| Soil Type | 20% | Compares user's soil texture with plant's soil preference |
| Available Space | 20% | Evaluates whether user's available space accommodates the plant |

Each recommendation includes:
- Compatibility score (0–100%)
- Matched factors (why the plant was recommended)
- Unmatched factors (considerations for the user)
- Basic care information

The system is fully deterministic and explainable — no black-box ML models.

## 🗄️ Database Schema

| Table | Primary Key | Key Columns |
|-------|-------------|-------------|
| `users` | `user_id` | `name`, `email` (unique), `location`, `created_at`, `updated_at` |
| `plants` | `plant_id` | `name` (unique), `scientific_name`, `soil_type`, `climate`, `sunlight`, `water_needs`, `space_requirement`, `description`, `image_url`, `created_at`, `updated_at` |
| `recommendations` | `rec_id` | `user_id` (FK), `plant_id` (FK), `search_id` (FK), `match_score`, `notes`, `timestamp` |
| `search_history` | `history_id` | `user_id` (FK), `soil_type`, `climate`, `sunlight`, `water_needs`, `space_requirement`, `location`, `query_text`, `results_count`, `timestamp` |

**Relationships:** User → Recommendations → Plant, User → SearchHistory → Recommendations

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Backend and PostgreSQL health status |
| `GET` | `/api/info` | System capabilities and metadata |
| `GET` | `/api/plants` | Paginated plant catalog |
| `GET` | `/api/plants/search?q=<query>` | Search plants by name, soil, climate, sunlight |
| `GET` | `/api/plants/<id>` | Plant details by ID |
| `POST` | `/api/recommendations/generate` | Generate ranked plant recommendations |
| `GET` | `/api/recommendations/<user_id>` | User recommendation history |
| `GET` | `/api/recommendations/history` | Recent recommendation history |

### Example Recommendation Request
```json
{
  "soil_type": "Sandy",
  "climate": "Warm/Dry",
  "sunlight": "Full Sun",
  "space": "Minimal",
  "limit": 5,
  "user_id": 1,
  "enrich": false
}
```

## 🔌 External Botanical API

GROWIT integrates with the **Perenual Plant API** (https://perenual.com/docs/api) for:
- Plant images and thumbnails
- Scientific names and common names
- Detailed care instructions
- Indoor/outdoor suitability
- Pet toxicity information

The external API is **optional** — the application functions fully using the local PostgreSQL database when the API is unavailable or unconfigured. API keys are stored exclusively in environment variables.

## 📁 Project Structure

```text
Crop_Recommendation/
├── Procfile                      # Process declaration for cloud platforms
├── render.yaml                   # Render deployment blueprint
├── railway.json                  # Railway deployment configuration
├── alembic.ini                   # Alembic migration configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── README.md                     # Project documentation
│
├── backend/                      # Flask Backend REST API
│   ├── app.py                   # Flask Application Factory
│   ├── config.py                # Environment-based configuration
│   ├── api/
│   │   └── routes.py            # REST API endpoints
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine and session management
│   │   ├── manage.py            # Database CLI management tool
│   │   ├── seed.py              # Plant catalog and demo data seeder
│   │   └── models/              # SQLAlchemy ORM Models
│   │       ├── user.py
│   │       ├── plant.py
│   │       ├── recommendation.py
│   │       └── search_history.py
│   ├── services/
│   │   ├── plant_service.py     # Plant retrieval and search
│   │   ├── plant_api_service.py # External API orchestration
│   │   └── recommendation_service.py
│   ├── recommendation/
│   │   └── engine.py            # Content-based scoring engine
│   ├── integrations/
│   │   ├── perenual_client.py   # Perenual API HTTP client
│   │   └── schema.py            # Normalized plant schema
│   └── utils/
│       └── response.py          # JSON response formatters
│
├── frontend/                     # Streamlit Frontend
│   ├── app.py                   # Streamlit application
│   ├── config.py                # Frontend configuration
│   ├── components/
│   │   └── ui.py                # UI components and design system
│   └── services/
│       └── api_client.py        # HTTP client for Flask API
│
├── migrations/                   # Alembic database migrations
│   └── versions/
│       └── 001_initial_schema.py
│
└── tests/                        # Automated tests
    ├── conftest.py
    ├── test_recommendation_engine.py
    ├── test_recommendation_api.py
    ├── test_recommendation_history.py
    ├── test_plant_api_service.py
    ├── test_api_client.py
    ├── test_database.py
    └── test_backend_verification.py
```

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (or SQLite for development)
- Git

### Setup
```bash
git clone https://github.com/your-username/Crop_Recommendation.git
cd Crop_Recommendation

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/plant_db` | PostgreSQL connection string |
| `FLASK_ENV` | No | `development` | Environment mode |
| `SECRET_KEY` | Yes (prod) | `dev-secret-key...` | Session signing key |
| `BACKEND_API_URL` | Yes | `http://localhost:5000/api/v1` | Flask API URL for Streamlit |
| `PERENUAL_API_KEY` | No | — | Perenual botanical API key |
| `PLANT_API_KEY` | No | — | Generic plant API key alias |

> **⚠️ Never commit `.env` or files containing real API keys to source control.**

## 🚀 Running the Backend

```bash
# Initialize database
python -m backend.database.manage init

# Seed sample plants
python -m backend.database.manage seed

# Start Flask server
python -m flask --app backend.app run --port 5000
```

Verify: http://localhost:5000/api/health

## 🖥️ Running the Frontend

In a separate terminal:

```bash
streamlit run frontend/app.py
```

Open: http://localhost:8501

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_recommendation_engine.py -v
python -m pytest tests/test_backend_verification.py -v
```

## ⚠️ Limitations

1. The recommendation engine uses rule-based weighted scoring, not machine learning.
2. The plant database is pre-seeded with ~30 curated plants; real-world deployment would require a larger dataset.
3. External API (Perenual) has rate limits on the free tier.
4. User authentication is lightweight (profile-based, no password/session security).
5. SQLite is used as a development fallback; PostgreSQL is required for production.

## 🔮 Future Scope

1. Machine learning-based recommendation model trained on user feedback data.
2. Plant disease detection using computer vision.
3. Mobile application (React Native or Flutter).
4. IoT sensor integration for real-time soil and climate monitoring.
5. Community features — user reviews and plant care tips sharing.
6. Multi-language support.

---

**GROWIT – Plant Recommendation Website** | College Mini Project
