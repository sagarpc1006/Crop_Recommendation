"""Application configuration module.

Supports environment-based configuration for Development, Production, and Testing.
Integrates with python-dotenv and normalizes cloud database connection strings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root if it exists
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


def normalize_database_url(url: str | None) -> str:
    """Normalize database connection URLs for SQLAlchemy.
    
    Render, Railway, and Heroku often provide URLs starting with 'postgres://',
    which SQLAlchemy 1.4+ / 2.0 requires to be 'postgresql://'.
    """
    if not url:
        # Fallback to local default if nothing is specified
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "plant_db")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    """Base configuration settings shared across environments."""
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-plant-recommendation")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    
    # Database
    DATABASE_URL: str = normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
        if origin.strip()
    ]
    
    # External API Keys (for future phases)
    PERENUAL_API_KEY: str | None = os.getenv("PERENUAL_API_KEY")
    TREFLE_API_KEY: str | None = os.getenv("TREFLE_API_KEY")


class DevelopmentConfig(BaseConfig):
    """Development configuration with debugging enabled."""
    DEBUG: bool = True
    TESTING: bool = False


class ProductionConfig(BaseConfig):
    """Production configuration optimized for cloud platforms (Render / Railway)."""
    DEBUG: bool = False
    TESTING: bool = False


class TestingConfig(BaseConfig):
    """Testing configuration with separate in-memory or test database."""
    DEBUG: bool = True
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"


# Configuration mapping dictionary
config_by_name: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> type[BaseConfig]:
    """Retrieve configuration class based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)
