# FloraMatch — Plant Recommendation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/backend-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit%201.35-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-orange.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-brightgreen.svg)](tests/)

FloraMatch is an end-to-end, production-ready web application providing transparent, explainable plant recommendations based on environmental growing criteria: **soil type**, **climate**, **sunlight availability**, and **available space**.

The application features a decoupled architecture: an interactive **Streamlit frontend**, a robust **Flask REST API**, a deterministic **Recommendation Engine**, a persistent **PostgreSQL relational database** with **Alembic migrations**, and external botanical data enrichment via the **Perenual API**.

---

## 🏛️ System Architecture

```text
User
 ↓
Streamlit Frontend (Port 8501)
 ↓  HTTP REST requests (JSON)
Flask REST API (Port 5000)
 ↓  Criteria evaluation & scoring
Recommendation Engine (Deterministic 4-Pillar Algorithm)
 ↓  Candidate query & persistent history
PostgreSQL Database (Users, Plants, Recommendations, Search History)
 ↓  External enrichment (cached with fallback)
External Plant API (Perenual API)
```

### Architectural Responsibilities

| Component | Technology | Primary Role |
| :--- | :--- | :--- |
| **Streamlit Frontend** | Streamlit, Requests, Custom CSS | Interactive UI, recommendation wizard, multi-criteria plant search, plant details view, and "My History" table/cards. |
| **Flask REST API** | Flask 3.0, Flask-CORS, Gunicorn | Exposes structured REST endpoints under `/api` and `/api/v1`, validates payloads, handles errors, and returns standard JSON response envelopes. |
| **Recommendation Engine** | Python Dataclasses | Deterministic scoring algorithm evaluating Climate (30%), Sunlight (30%), Soil (20%), and Space (20%) with explainability factors. |
| **PostgreSQL Database** | PostgreSQL, SQLAlchemy 2.0, Alembic | Persistent storage of plant catalog, user profiles, search criteria, and recommendation history records with connection pooling. |
| **External Plant API** | Requests, In-Process TTL Cache | Supplements local catalog with images and detailed care instructions via Perenual API with resilient offline fallback. |

---

## 📁 Repository Structure

```text
Crop_Recommendation/
├── Procfile                      # Process declaration for cloud platforms (Render/Railway)
├── render.yaml                   # Infrastructure as Code Blueprint for Render
├── railway.json                  # Deployment configuration for Railway
├── alembic.ini                   # Alembic database migration configuration
├── requirements.txt              # Production and development dependencies
├── .env.example                  # Safe environment variable configuration template
├── .gitignore                    # Git ignore file for secrets and environments
├── README.md                     # Project documentation & operational manual
│
├── backend/                      # Python Flask Backend REST API
│   ├── app.py                   # Flask Application Factory & Server Entry Point
│   ├── config.py                # Environment-based configuration (Dev/Prod/Test)
│   ├── api/                     # REST API Blueprint routes
│   │   ├── __init__.py
│   │   └── routes.py            # API Endpoints (/health, /plants, /recommendations)
│   ├── database/                # Database connection, models, CLI, and seed script
│   │   ├── __init__.py
│   │   ├── connection.py        # SQLAlchemy engine, session maker, connection pool
│   │   ├── manage.py            # Database CLI management tool
│   │   ├── seed.py              # Sample plants and demonstration data seeder
│   │   └── models/              # SQLAlchemy ORM Models
│   │       ├── user.py          # User model (users table)
│   │       ├── plant.py         # Plant model (plants table with unique name index)
│   │       ├── recommendation.py# Recommendation model (recommendations table)
│   │       └── search_history.py# SearchHistory model (search_history table)
│   ├── services/                # Business logic layer
│   │   ├── plant_service.py     # Plant retrieval and query operations
│   │   ├── plant_api_service.py # External plant API orchestrator & caching
│   │   └── recommendation_service.py # Recommendation generator & DB logger
│   ├── recommendation/          # Recommendation engine package
│   │   └── engine.py            # Scoring heuristics, weights, and criteria dataclass
│   ├── integrations/            # External API client implementations
│   │   ├── perenual_client.py   # Perenual API HTTP client
│   │   └── schema.py            # Normalized plant schema
│   └── utils/                   # Shared utilities
│       └── response.py          # Standardized JSON response envelopes
│
├── frontend/                     # Streamlit Frontend Web Application
│   ├── app.py                   # Streamlit Application Entry Point & Navigation Router
│   ├── config.py                # Frontend configuration & backend URL resolution
│   ├── components/              # Reusable UI widgets and custom CSS design system
│   │   └── ui.py                # UI components, cards, tables, status indicators
│   └── services/                # HTTP API Client communicating with Flask
│       └── api_client.py        # Safe, structured REST client
│
├── migrations/                   # Alembic database migrations
│   ├── env.py                   # Alembic runtime environment
│   ├── script.py.mako           # Migration version template
│   └── versions/                # Migration revisions
│       └── 001_initial_schema.py# Initial schema creation (users, plants, etc.)
│
└── tests/                        # Automated unit and integration tests (65 tests)
    ├── test_backend_verification.py # 11 critical project verification test cases
    ├── test_recommendation_history.py # Recommendation persistence & history tests
    ├── test_recommendation_api.py   # REST API endpoint tests
    ├── test_recommendation_engine.py# Scoring algorithm & heuristic tests
    ├── test_plant_api_service.py    # External API caching and fallback tests
    ├── test_api_client.py           # Frontend API client tests
    └── test_database.py             # Database models, relationships, and constraints
```

---

## ⚙️ Environment Variables Documentation

All sensitive credentials and environment configurations are managed via environment variables. Copy `.env.example` to `.env` for local execution:

```bash
cp .env.example .env
```

| Variable Name | Required | Default / Example | Description |
| :--- | :--- | :--- | :--- |
| **`FLASK_ENV`** | No | `development` | Environment mode (`development`, `production`, `testing`). |
| **`SECRET_KEY`** | Yes (in prod) | `dev-secret-key...` | Cryptographic secret for signing session cookies. |
| **`CORS_ORIGINS`** | No | `http://localhost:8501` | Allowed origins for CORS (comma-separated). |
| **`DATABASE_URL`** | Yes | `postgresql://user:pass@host:5432/dbname` | Full PostgreSQL connection string (auto-normalized). |
| **`BACKEND_API_URL`**| Yes | `http://localhost:5000/api/v1` | URL the Streamlit frontend uses to call Flask. |
| **`PLANT_API_KEY`** | No | `sk-...` | Optional API key for Perenual botanical data. |
| **`PLANT_API_TIMEOUT`**| No | `8` | External API HTTP timeout in seconds. |
| **`PLANT_API_CACHE_TTL`**| No| `300` | In-memory cache duration for external API (seconds). |

> [!CAUTION]
> Never commit `.env` or any file containing real database passwords, secret keys, or API tokens to source control. `.env` is ignored by `.gitignore`.

---

## 🚀 Local Development Setup

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11, 3.12, 3.13)
- **PostgreSQL 14+** (Local service or Docker container)
- **Git**

### 2. Clone and Setup Environment
```bash
git clone https://github.com/your-username/Crop_Recommendation.git
cd Crop_Recommendation

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database and Seed Data
Ensure PostgreSQL is running and your `plant_db` database exists:
```bash
# Apply migrations using Alembic
python -m alembic upgrade head

# Seed sample botanical catalog and demonstration user
python -m backend.database.seed
```

### 4. Run the Backend API Server
```bash
# Starts Flask development server on http://localhost:5000
python -m flask --app backend.app run --port 5000
```
Verify the API is operational by browsing to:
`http://localhost:5000/api/health`

### 5. Run the Streamlit Frontend
In a new terminal window (with virtual environment active):
```bash
# Starts Streamlit app on http://localhost:8501
streamlit run frontend/app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

FloraMatch includes a comprehensive suite of **65 automated unit and integration tests** covering models, API endpoints, recommendation heuristics, error states, and history persistence.

```bash
# Run all tests
python -m pytest tests/ -v

# Run the 11 critical verification test cases specifically
python -m pytest tests/test_backend_verification.py -v
```

### Test Coverage Highlights
- ✅ **Valid Recommendation Request**: Ensures 200 response with ranked items and factor explainability.
- ✅ **Missing Soil Type & Missing Climate**: Verifies graceful handling and fallback defaults without error.
- ✅ **Invalid Sunlight & Invalid Space**: Validates safe handling of unknown user inputs.
- ✅ **No Matching Plants**: Tests safe return of empty recommendation list `[]`.
- ✅ **Plant Search**: Verifies multi-attribute queries across Name, Soil, Climate, and Sunlight.
- ✅ **Plant Details**: Validates complete details and HTTP 404 for invalid IDs.
- ✅ **Database Offline Fallback**: Verifies seamless fallback to in-memory `SAMPLE_PLANTS` when database connectivity drops.
- ✅ **External API Unavailable Fallback**: Verifies local catalog works completely without external API keys.
- ✅ **Recommendation History & Duplicate Prevention**: Verifies persistence to PostgreSQL and prevention of redundant records.

---

## 🌐 Production Deployment Guide

You can deploy FloraMatch to **Render** or **Railway** with high availability and automated builds.

---

### Option A: Deployment to Render (Recommended)

Render provides native PostgreSQL databases and managed Web Services with free-tier support.

#### Step 1: Push Repository to GitHub
Ensure all code and configuration files (`render.yaml`, `Procfile`, `requirements.txt`) are committed and pushed to your GitHub repository.

#### Step 2: Create a Render PostgreSQL Database
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **PostgreSQL**.
3. Name: `floramatch-db`
4. Database Name: `plant_db`
5. User: `postgres`
6. Plan: **Free**
7. Click **Create Database**.
8. Once provisioned, copy the **Internal Database URL** (e.g. `postgresql://postgres:...@dpg-...-a:5432/plant_db`).

#### Step 3: Deploy Backend Web Service
1. Click **New +** → **Web Service** → Connect your GitHub repository.
2. Name: `floramatch-backend`
3. Runtime: **Python**
4. Build Command:
   ```bash
   pip install -r requirements.txt && python -m alembic upgrade head && python -m backend.database.seed
   ```
5. Start Command:
   ```bash
   gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```
6. Add Environment Variables:
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = *(Paste Internal Database URL from Step 2)*
   - `SECRET_KEY` = *(Generate a 32-character random string)*
   - `CORS_ORIGINS` = `https://floramatch-frontend.onrender.com,http://localhost:8501`
   - `PLANT_API_KEY` = *(Optional: your Perenual API key)*
7. Click **Create Web Service**. Note your backend URL (e.g. `https://floramatch-backend.onrender.com`).

#### Step 4: Deploy Streamlit Frontend Web Service
1. Click **New +** → **Web Service** → Connect the same GitHub repository.
2. Name: `floramatch-frontend`
3. Runtime: **Python**
4. Build Command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start Command:
   ```bash
   streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```
6. Add Environment Variables:
   - `BACKEND_API_URL` = `https://floramatch-backend.onrender.com/api/v1`
   - `API_TIMEOUT_SECONDS` = `10`
7. Click **Create Web Service**.

---

### Option B: Deployment to Railway

#### Step 1: Create a Railway Project
1. Log in to [Railway](https://railway.app/).
2. Click **New Project** → **Provision PostgreSQL**.
3. Railway automatically creates a PostgreSQL instance and exposes `DATABASE_URL`.

#### Step 2: Deploy Backend Service
1. In the same project, click **New** → **GitHub Repo** → select repository.
2. Go to **Settings** → Set **Service Name** to `backend`.
3. Set **Start Command**:
   ```bash
   python -m alembic upgrade head && python -m backend.database.seed && gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```
4. Set **Variables**:
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` *(Reference Railway's PostgreSQL variable)*
   - `SECRET_KEY` = *(Random secret)*
   - `CORS_ORIGINS` = `*`
   - `PLANT_API_KEY` = *(Optional: Perenual key)*
5. Generate a public domain under **Settings** → **Networking** (e.g. `https://floramatch-backend.up.railway.app`).

#### Step 3: Deploy Frontend Service
1. In the same project, click **New** → **GitHub Repo** → select same repository.
2. Go to **Settings** → Set **Service Name** to `frontend`.
3. Set **Start Command**:
   ```bash
   streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```
4. Set **Variables**:
   - `BACKEND_API_URL` = `https://floramatch-backend.up.railway.app/api/v1`
   - `API_TIMEOUT_SECONDS` = `10`
5. Generate a public domain under **Settings** → **Networking**.

---

## 📡 API Reference Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Backend and PostgreSQL database health status check. |
| `GET` | `/api/info` | Capabilities, endpoints, and external API metadata. |
| `GET` | `/api/plants` | Paginated catalog of all plants in database. |
| `GET` | `/api/plants/search?q=<query>` | Multi-criteria search across Name, Soil, Climate, Sunlight. |
| `GET` | `/api/plants/<plant_id>` | Detailed plant information with care requirements and optional external API enrichment. |
| `POST` | `/api/recommendations/generate` | Generates ranked recommendations, scores, and persists to history. |
| `GET` | `/api/recommendations/<user_id>` | Retrieves persistent recommendation history for a specific user. |
| `GET` | `/api/recommendations/history` | Retrieves recent recommendation records across sessions. |

### Example Recommendation Payload (`POST /api/recommendations/generate`):
```json
{
  "soil_type": "Sandy",
  "climate": "Warm/Dry",
  "sunlight": "Full Sun",
  "space": "Minimal",
  "limit": 3,
  "user_id": 1,
  "enrich": false
}
```

---

## 🔒 Security Best Practices Implemented

1. **No Hardcoded Secrets**: All database connection strings, passwords, and external API tokens are read exclusively from environment variables.
2. **Safe Client Communication**: Streamlit never accesses PostgreSQL directly; all database interaction is mediated by Flask backend services.
3. **External API Key Concealment**: Third-party API keys (Perenual) are stored strictly on the backend and never exposed to the browser or Streamlit client.
4. **Resilient Offline Fallback**: If PostgreSQL or external APIs are unreachable, the system returns curated fallback data without unhandled exceptions.
5. **CORS Restrictions**: Flask CORS is locked down to configurable origins in production.
6. **Input Sanitization**: Recommendation criteria and search queries are sanitized and safe against SQL injection via SQLAlchemy ORM parameterized queries.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
