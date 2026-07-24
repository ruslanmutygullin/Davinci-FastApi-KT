"""Shared test setup. The key idea: override get_session so tests use a throwaway
in-memory database instead of the real notes.db file — no change to app code.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session


@pytest.fixture(name="client")
def client_fixture():
    # A brand-new in-memory database for every test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared connection for the in-memory DB
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    # Swap the real session dependency for the test one.
    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()  # reset so tests don't leak into each other
