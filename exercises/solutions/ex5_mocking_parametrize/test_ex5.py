"""Exercise 5 — SOLUTION."""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from unittest.mock import patch

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def fresh_db():
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(main.engine)
    SQLModel.metadata.create_all(main.engine)
    yield


# --- TODO 1 solution: parametrize blank title validation ---

@pytest.mark.parametrize("title", ["", "   ", "\t"])
def test_blank_titles_rejected(title):
    with pytest.raises(ValidationError):
        main.NoteCreate(title=title)


# --- TODO 2 solution: parametrize endpoint status codes ---

@pytest.mark.parametrize("payload,expected_status", [
    ({"title": "valid"}, 201),
    ({"title": "  also valid  "}, 201),
    ({"title": ""}, 422),
    ({"title": "   "}, 422),
])
def test_create_endpoint_payloads(payload, expected_status):
    assert client.post("/notes", json=payload).status_code == expected_status


# --- TODO 3 solution: unknown fields rejected ---

def test_patch_rejects_unknown_fields():
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    assert client.patch(f"/notes/{nid}", json={"titl": "typo"}).status_code == 422


# --- TODO 4 solution: webhook called when URL is set ---

def test_notify_called_on_create(monkeypatch):
    monkeypatch.setattr(main, "WEBHOOK_URL", "http://test.example.com")
    with patch("main.httpx.post") as mock_post:
        r = client.post("/notes", json={"title": "x"})
        assert r.status_code == 201
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        assert url == "http://test.example.com"


# --- TODO 5 solution: webhook not called when URL is empty ---

def test_notify_not_called_when_url_empty(monkeypatch):
    monkeypatch.setattr(main, "WEBHOOK_URL", "")
    with patch("main.httpx.post") as mock_post:
        client.post("/notes", json={"title": "x"})
        mock_post.assert_not_called()
