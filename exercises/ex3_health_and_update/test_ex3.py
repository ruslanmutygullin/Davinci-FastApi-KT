"""Spec for Exercise 3."""

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_update_existing_note():
    nid = client.post("/notes", json={"title": "old"}).json()["id"]
    r = client.put(f"/notes/{nid}", json={"title": "new", "done": True})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "new"
    assert body["done"] is True


def test_update_missing_note_is_404():
    assert client.put("/notes/9999", json={"title": "x", "done": False}).status_code == 404
