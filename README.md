# FloraMatch - Plant Recommendation System

A modular, production-ready web application designed to recommend suitable plants based on environmental growing conditions (soil type, climate, sunlight availability, and available space).

The system features a **Streamlit** frontend, a **Python Flask** REST API backend, and a **PostgreSQL** relational database layer orchestrated with **SQLAlchemy 2.0+** and **Alembic**.

---

## 🏗️ Architecture & Folder Structure

```
Crop_Recommendation/
├── alembic.ini                   # Alembic database migration configuration
├── requirements.txt              # Project dependencies (Flask, Streamlit, SQLAlchemy, Alembic)
├── .env.example                  # Environment variable configuration template
├── .gitignore                    # Git ignore file for Python, environments, and secrets
├── README.md                     # Project documentation & operational manual
│
├── backend/                      # Python Flask Backend REST API
│   ├── app.py                   # Flask Application Factory & Server Entry Point
│   ├── config.py                # Environment-based configuration (Dev/Prod/Test)
│   ├── api/                     # REST API Blueprint routes
│   │   ├── __init__.py
│   │   └── routes.py            # API Endpoints (/health, /info, /plants, /recommendations)
│   ├── database/                # Database connection, models, CLI, and seed script
│   │   ├── __init__.py
│   │   ├── connection.py        # SQLAlchemy engine, session maker, connection pool
│   │   ├── manage.py            # Database CLI management tool (init, migrate, seed, status, reset)
│   │   ├── seed.py              # Sample plants and demonstration data seeder
│   │   └── models/              # SQLAlchemy ORM Models
│   │       ├── __init__.py
│   │       ├── user.py          # User model (users table)
│   │       ├── plant.py         # Plant model (plants table with unique name index)
│   │       ├── recommendation.py# Recommendation model (recommendations table)
│   │       └── search_history.py# SearchHistory model (search_history table)
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── plant_service.py     # Plant retrieval and query operations
│   ├── recommendation/          # Recommendation engine package
│   │   ├── __init__.py
│   │   └── engine.py            # Recommendation criteria dataclass & engine interface
│   ├── integrations/            # External Botanical API integrations (scaffolded)
│   │   ├── __init__.py
│   │   └── perenual_client.py   # Perenual & Trefle API client interfaces
│   └── utils/                   # Shared backend utilities
│       ├── __init__.py
│       └── response.py          # Standardized JSON response envelopes
│
├── frontend/                     # Streamlit Frontend Web Application
│   ├── app.py                   # Streamlit Application Entry Point
│   ├── config.py                # Frontend configuration & backend URL resolution
│   ├── components/              # Reusable UI widgets and custom CSS
│   │   ├── __init__.py
│   │   └── ui.py                # Header banners, status cards, and layout styles
│   └── services/                # Frontend API client layer
│       ├── __init__.py
│       └── api_client.py        # HTTP client communicating with Flask REST API
│
├── migrations/                   # Alembic database migrations
│   ├── env.py                   # Alembic migration runtime environment
│   ├── script.py.mako           # Migration version template
│   └── versions/                # Generated migration revisions
│       └── 001_initial_schema.py# Initial schema creation (users, plants, etc.)
│
└── tests/                        # Automated unit and integration tests
    └── test_database.py         # Database model, constraint, cascade, and seed tests
```

---

## 📂 Purpose of Each Folder

| Folder | Purpose |
| :--- | :--- |
| **`backend/`** | Hosts the Flask application, REST controllers, database layer, business logic, and modular sub-packages. |
| **`backend/api/`** | Implements REST endpoints (`routes.py`) with clean status codes and structured response envelopes. |
| **`backend/database/`** | Encapsulates PostgreSQL connectivity (`connection.py`), ORM entities (`models/`), seeding (`seed.py`), and CLI utilities (`manage.py`). |
| **`backend/services/`** | Isolates business logic from view routes to maintain clean separation of concerns. |
| **`backend/recommendation/`** | Houses the recommendation orchestrator and algorithm heuristics (decoupled for future ML/scoring). |
| **`backend/integrations/`** | Pre-configured client stubs for external plant APIs (e.g., Perenual, Trefle). |
| **`backend/utils/`** | Reusable helpers, including consistent JSON response formatting (`api_response`, `error_response`). |
| **`frontend/`** | Streamlit application providing interactive web interface, diagnostics, and catalog preview. |
| **`frontend/components/`** | Modular UI components (headers, status indicators, badges, custom CSS styling). |
| **`frontend/services/`** | HTTP communication layer (`BackendApiClient`) connecting Streamlit to Flask. |
| **`migrations/`** | Alembic migration scripts tracking database schema revisions over time. |
| **`tests/`** | Automated test suites verifying database models, constraints, and business logic. |

---

## 🔄 How Frontend Communicates with Backend

1. The **Streamlit Frontend** runs as an independent process (default: `http://localhost:8501`).
2. When the frontend loads or a user submits input, **`BackendApiClient`** ([`frontend/services/api_client.py`](frontend/services/api_client.py)) issues standard HTTP requests (`GET`, `POST`) via Python `requests` to the **Flask REST API** (`http://localhost:5000/api/v1`).
3. Flask validates the request, queries PostgreSQL through SQLAlchemy, and wraps the payload in a standard JSON envelope:
   ```json
   {
     "success": true,
     "message": "Service health report",
     "data": { ... },
     "meta": null
   }
   ```
4. The frontend unpacks the JSON response and reactively renders the UI cards, status indicators, or recommendation lists.
5. Cross-Origin Resource Sharing (**CORS**) is enabled on Flask via `flask_cors` to permit seamless communication between Streamlit and Flask.

---

## 🗄️ How PostgreSQL is Connected

1. **Environment Variables**: The database connection string is read from the `DATABASE_URL` environment variable defined in `.env`:
   ```ini
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/plant_db
   ```
   *(If `DATABASE_URL` is omitted, `backend/config.py` automatically constructs the URL from individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` variables).*
2. **SQLAlchemy 2.0+ Engine**: [`backend/database/connection.py`](backend/database/connection.py) initializes a connection engine with:
   - `pool_pre_ping=True`: Validates connections before using them, preventing stale connection errors.
   - `pool_recycle=300`: Automatically recycles connections every 5 minutes (critical for Render/Railway cloud environments).
3. **Resilient Health Check**: On startup, [`check_db_connection()`](backend/database/connection.py) pings the database (`SELECT 1`). If PostgreSQL is temporarily offline, the API starts safely and flags the database status without crashing.

---

## 🚀 Setup & Local Execution Guide

### 1. Python Virtual Environment Setup

**Windows (PowerShell):**
```powershell
# Navigate into the project folder
cd Crop_Recommendation

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd Crop_Recommendation
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and set your PostgreSQL credentials:

```powershell
copy .env.example .env
```

Edit `.env` to match your local setup:
```ini
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/plant_db
BACKEND_API_URL=http://localhost:5000/api/v1
```

### 4. Create & Initialize PostgreSQL Database

Create the database in PostgreSQL:
```sql
CREATE DATABASE plant_db;
```

Apply migrations and seed initial sample plants:
```powershell
# Run Alembic migrations
python -m backend.database.manage migrate

# Seed sample plants (Aloe Vera, Money Plant, Tulsi, Snake Plant, Marigold)
python -m backend.database.manage seed

# Verify table counts and catalog status
python -m backend.database.manage status
```

### 5. Run the Automated Tests
```powershell
python -m unittest tests/test_database.py -v
```

### 6. Run the Application Locally

Open two terminal windows (with your virtual environment activated):

**Terminal 1 — Start Flask REST Backend:**
```powershell
python -m backend.app
# Backend runs at http://127.0.0.1:5000
```

**Terminal 2 — Start Streamlit Frontend:**
```powershell
streamlit run frontend/app.py
# Frontend opens at http://localhost:8501
```

---

## ☁️ Cloud Deployment Readiness (Render / Railway)

The project structure is natively configured for cloud container / PaaS deployment:
- **Backend**: Can be deployed as a web service running `gunicorn backend.app:app`.
- **Database**: Works out of the box with managed PostgreSQL instances (automatically handles `postgres://` to `postgresql://` URI normalization).
- **Frontend**: Can be deployed as a standalone Streamlit web service pointing to the backend's public URL via the `BACKEND_API_URL` environment variable.
