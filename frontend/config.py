"""Frontend configuration module."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Backend REST API endpoint configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000/api/v1").rstrip("/")
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "5"))

# Application visual metadata
APP_TITLE = "GROWIT – Plant Recommendation Website"
APP_TAGLINE = "Smart plant recommendations tailored to your soil, climate, sunlight, and space."
