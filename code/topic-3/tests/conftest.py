"""Shared test fixtures for Topic 3.

Three fixtures:
- `client`          — TestClient with auth faked; use for endpoint integration tests
- `real_auth_client`— TestClient with real JWT flow; use to test auth itself
- `db`              — raw Session for direct service tests (no HTTP)
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.dependencies import get_session
from app.auth import get_current_user


def _make_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="client")
def client_fixture():
    engine = _make_engine()

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = lambda: "test-user"

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name="real_auth_client")
def real_auth_client_fixture():
    """Like `client`, but WITHOUT faking auth — used to test the real JWT flow."""
    engine = _make_engine()

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name="db")
def db_fixture():
    """A raw Session for calling service functions directly — no HTTP overhead."""
    engine = _make_engine()
    with Session(engine) as session:
        yield session
