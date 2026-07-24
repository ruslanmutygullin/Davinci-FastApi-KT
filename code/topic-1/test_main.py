"""Reference tests for Topic 1. All of these pass — run `pytest -v` to see the behavior.

The in-memory `notes` dict is module-global, so we reset it between tests with a fixture
to keep them independent.
"""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_store():
    main.notes.clear()
    main._next_id = 1
    yield


client = TestClient(main.app)


def test_create_returns_201_with_id():
    r = client.post("/notes", json={"title": "Buy milk"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Buy milk"
    assert body["done"] is False
    assert body["id"] == 1


def test_get_after_create():
    created = client.post("/notes", json={"title": "x"}).json()
    r = client.get(f"/notes/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "x"


def test_missing_note_is_404():
    assert client.get("/notes/999").status_code == 404


def test_bad_body_is_422():
    # title must be a string; a dict is invalid, and an empty body is missing title
    assert client.post("/notes", json={"title": {"nested": 1}}).status_code == 422
    assert client.post("/notes", json={}).status_code == 422


def test_list_filter_by_done():
    client.post("/notes", json={"title": "a", "done": True})
    client.post("/notes", json={"title": "b", "done": False})
    assert len(client.get("/notes").json()) == 2
    assert len(client.get("/notes", params={"done": True}).json()) == 1


def test_update_and_delete():
    nid = client.post("/notes", json={"title": "old"}).json()["id"]

    updated = client.put(f"/notes/{nid}", json={"title": "new", "done": True})
    assert updated.json()["title"] == "new"
    assert updated.json()["done"] is True

    assert client.delete(f"/notes/{nid}").status_code == 204
    assert client.get(f"/notes/{nid}").status_code == 404
