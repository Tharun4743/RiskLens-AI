"""SQLAlchemy 2.0 Database Manager and Connection Pool for PostgreSQL & SQLite.
Supports Vercel serverless execution with safe connection pooling and automatic dialect normalization.
"""
import os
import logging
from contextlib import contextmanager
from typing import Generator, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base

logger = logging.getLogger("risklens.database")

DEFAULT_SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "risklens.db"
)


def get_database_url() -> str:
    """Resolve and normalize database URL for PostgreSQL or local SQLite."""
    raw_url = os.environ.get("DATABASE_URL", "").strip()

    if not raw_url:
        # Fallback to local SQLite for seamless offline development and clean clones
        db_path = os.environ.get("RISKLENS_DB_PATH", DEFAULT_SQLITE_PATH)
        return f"sqlite:///{db_path}"

    # Vercel / Cloud providers often provide 'postgres://' or 'postgresql://'
    # Normalize to SQLAlchemy 2.0 psycopg3 dialect: 'postgresql+psycopg://'
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return raw_url


DATABASE_URL = get_database_url()
IS_POSTGRES = "postgres" in DATABASE_URL

# Configure engine with serverless-safe connection pooling
if IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,      # Discard stale connections
        pool_size=5,             # Conservative connection limit for serverless lambdas
        max_overflow=10,         # Allow burst traffic
        pool_recycle=300,        # Recycle connections every 5 minutes
        echo=False
    )
    logger.info("Initialized PostgreSQL database engine with connection pooling.")
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=False
    )
    logger.info("Initialized SQLite database engine at %s", DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for transactional database sessions with automatic commit/rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.error("Database transaction rolled back due to error: %s", exc)
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    with get_db_session() as session:
        yield session


def init_db():
    """Create database tables and indexes if they do not exist.
    Safely applies backwards-compatible column additions.
    Never drops existing production data.
    """
    try:
        Base.metadata.create_all(bind=engine)
        # Verify and add columns to customers table if upgrading schema
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE customers ADD COLUMN profile TEXT"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE customers ADD COLUMN expected_result TEXT"))
                conn.commit()
            except Exception:
                pass
        logger.info("Database schema verified/initialized successfully (Engine: %s).", engine.dialect.name)
    except Exception as exc:
        logger.error("Failed to initialize database schema: %s", exc)
        raise



def check_db_connection() -> Dict[str, Any]:
    """Verify active database connectivity and Supabase connection for health check."""
    supabase_configured = bool(os.environ.get("SUPABASE_URL") and (os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_PUBLISHABLE_KEY")))
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "dialect": engine.dialect.name,
            "is_postgres": IS_POSTGRES,
            "supabase": "configured" if supabase_configured else "not_configured"
        }
    except Exception as exc:
        logger.warning("Database connectivity check failed: %s", exc)
        return {
            "status": "disconnected",
            "dialect": engine.dialect.name,
            "supabase": "configured" if supabase_configured else "not_configured",
            "error": str(exc)
        }

