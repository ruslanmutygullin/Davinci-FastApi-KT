"""Database wiring — identical to Topic 2 except the URL now comes from settings."""

from sqlmodel import SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.database_url, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
