"""Exercise 2 spec — passes against the solution."""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_store():
    main.notes.clear()
    main._next_id = 1
    yield


client = TestClient(main.app)


def test_created_note_records_owner_from_dependency():
    r = client.post("/notes", json={"title": "mine"})
    assert r.status_code == 201
    assert r.json()["owner"] == "demo-user"


def test_dependency_is_overridable():
    main.app.dependency_overrides[main.get_current_user] = lambda: "someone-else"
    try:
        r = client.post("/notes", json={"title": "x"})
        assert r.json()["owner"] == "someone-else"
    finally:
        main.app.dependency_overrides.clear()
