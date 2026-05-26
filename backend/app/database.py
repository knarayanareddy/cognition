"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _create_engine():
    """Create database engine lazily to allow app startup without DB."""
    try:
        return create_engine(settings.database_url, pool_pre_ping=True)
    except Exception:
        return None


def _create_session_factory():
    """Create session factory lazily."""
    eng = _create_engine()
    if eng:
        return sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return None


def get_db():
    """Dependency that provides a database session."""
    factory = _create_session_factory()
    if not factory:
        # Return a mock-like None for development without DB
        yield None
        return
    db = factory()
    try:
        yield db
    finally:
        db.close()
