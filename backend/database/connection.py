"""PostgreSQL Database connection and session management module.

Uses SQLAlchemy 2.0+ declarative base and connection pooling.
Includes resilient health checks and safe initialization for cloud & local environments.
"""

import logging
from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config import get_config

logger = logging.getLogger(__name__)

# Declarative Base for all ORM models
Base = declarative_base()

# Engine and sessionmaker placeholders
_engine = None
_SessionFactory = None


def get_engine():
    """Get or initialize the SQLAlchemy engine with connection pooling."""
    global _engine
    if _engine is None:
        config = get_config()
        _engine = create_engine(
            config.DATABASE_URL,
            pool_pre_ping=True,  # Automatically tests connection freshness
            pool_recycle=300,    # Prevents dropped connections on cloud providers
            echo=(config.DEBUG and not getattr(config, "TESTING", False)),
        )
    return _engine


def get_session_factory():
    """Get or initialize the SQLAlchemy session factory."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """Yield a database session context, ensuring proper close and rollback on error."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_db_connection() -> dict[str, str | bool]:
    """Check database connectivity without raising unhandled exceptions.
    
    Returns:
        dict: Connection status details including success state and message.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "connected": True,
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return {
            "connected": False,
            "message": f"Database unreachable: {str(e)}"
        }


def init_db():
    """Initialize database tables defined on Base.
    
    Safe wrapper: Attempts table creation; logs warning if database is offline.
    """
    try:
        engine = get_engine()
        # Import models so Base metadata is populated
        import backend.database.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(
            f"Could not automatically initialize tables (PostgreSQL server may be offline): {e}"
        )
