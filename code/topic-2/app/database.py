"""Database wiring: the engine (one per app) and the per-request session dependency."""

from sqlmodel import SQLModel, Session, create_engine

# A local SQLite file — zero setup. Swap this URL for Postgres and nothing else changes.
DATABASE_URL = "sqlite:///./notes.db"

# The engine is a connection pool, created once for the whole application.
# echo=True logs every SQL statement — great for seeing what the ORM emits.
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    """Create tables. Called once on startup from the lifespan (see main.py)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a per-request session; the `with` block closes it after the response.

    This is a dependency (see routers/notes.py). Everything before `yield` is setup,
    the yielded value is injected, and everything after `yield` is teardown.
    """
    with Session(engine) as session:
        yield session
