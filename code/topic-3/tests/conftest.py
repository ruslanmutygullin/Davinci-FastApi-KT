"""Test setup for Topic 3.

We override TWO dependencies:
- get_session       -> in-memory test database (as in Topic 2)
- get_current_user  -> a fake user, so we can test protected routes without minting tokens

This is the payoff of auth-as-a-dependency: authentication becomes trivially fakeable.
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
    """Like `client`, but WITHOUT faking auth — used to test the real token flow."""
    engine = _make_engine()

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()
