"""Spec for Exercise 3. These FAIL against the starter and PASS once you complete the TODOs."""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlmodel import Session

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def fresh_db():
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(main.engine)
    SQLModel.metadata.create_all(main.engine)
    yield


# --- router tests (HTTP contract) ---

def test_create_returns_201(client=client):
    r = client.post("/notes", json={"title": "hello"})
    assert r.status_code == 201
    assert r.json()["title"] == "hello"


def test_create_strips_whitespace(client=client):
    r = client.post("/notes", json={"title": "  trimmed  "})
    assert r.status_code == 201
    assert r.json()["title"] == "trimmed"


def test_create_rejects_blank_title(client=client):
    assert client.post("/notes", json={"title": ""}).status_code == 422
    assert client.post("/notes", json={"title": "   "}).status_code == 422


def test_get_existing_note(client=client):
    nid = client.post("/notes", json={"title": "find me"}).json()["id"]
    r = client.get(f"/notes/{nid}")
    assert r.status_code == 200
    assert r.json()["title"] == "find me"


def test_get_missing_note_returns_custom_error(client=client):
    r = client.get("/notes/999")
    assert r.status_code == 404
    assert r.json() == {"error": "Note 999 does not exist"}


def test_patch_updates_only_sent_fields(client=client):
    nid = client.post("/notes", json={"title": "original"}).json()["id"]
    r = client.patch(f"/notes/{nid}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["title"] == "original"   # unchanged
    assert r.json()["done"] is True


def test_patch_rejects_unknown_fields(client=client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    assert client.patch(f"/notes/{nid}", json={"titl": "typo"}).status_code == 422


def test_patch_rejects_empty_body(client=client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    assert client.patch(f"/notes/{nid}", json={}).status_code == 422


# --- direct service tests (no HTTP) ---

def test_service_get_raises_for_missing():
    with Session(main.engine) as db:
        with pytest.raises(main.NoteNotFoundError):
            main.note_service.get(db, 999)


def test_service_create_and_patch(client=client):
    with Session(main.engine) as db:
        note = main.note_service.create(db, main.NoteCreate(title="  spaces  "))
        assert note.title == "spaces"

        patched = main.note_service.patch(db, note.id, main.NoteUpdate(done=True))
        assert patched.done is True
        assert patched.title == "spaces"   # untouched


# --- schema unit tests ---

def test_note_create_validator_rejects_blank():
    with pytest.raises(ValidationError):
        main.NoteCreate(title="")


def test_note_update_rejects_unknown():
    with pytest.raises(ValidationError):
        main.NoteUpdate(titl="typo")


def test_note_update_rejects_empty():
    with pytest.raises(ValidationError):
        main.NoteUpdate()
