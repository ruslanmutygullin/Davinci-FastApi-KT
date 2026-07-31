"""Database wiring: the engine (one per app) and the per-request session dependency."""

cfrom sqlmodel import SQLModel, create_engine

# A local SQLite file — zero setup. Swap this URL for Postgres and nothing else changes.
DATABASE_URL = "sqlite:///./notes.db"

# The engine is a connection pool, created once for the whole application.
# echo=True logs every SQL statement — great for seeing what the ORM emits.
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    """Create tables. Called once on startup from the lifespan (see main.py)."""
    SQLModel.metadata.create_all(engine)
