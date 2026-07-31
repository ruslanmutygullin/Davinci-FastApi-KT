"""Exercise 5 — mocking and parametrize.

GOAL: write the missing tests in this file. The app and service are already complete —
your job is to test them properly.

  1. Complete `test_blank_titles_rejected` using @pytest.mark.parametrize to test that
     all of ["", "   ", "\t"] produce a ValidationError from NoteCreate.

  2. Complete `test_create_endpoint_payloads` using @pytest.mark.parametrize to check
     that valid payloads return 201 and invalid ones return 422.
     Use at least: a valid title, an empty title, a whitespace-only title.

  3. Complete `test_patch_rejects_unknown_fields` — send an unknown field to the PATCH
     endpoint and assert you get 422.

  4. Complete `test_notify_called_on_create` — use patch() to intercept
     `httpx.post` in `main._notify` and assert it is called when webhook_url is set.
     Hint: use monkeypatch to set main.WEBHOOK_URL = "http://test.example.com" first.

  5. Complete `test_notify_not_called_when_url_empty` — assert httpx.post is NOT called
     when WEBHOOK_URL is "".

Run `pytest -v` to see what needs to pass.
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from unittest.mock import patch

import main

client = TestClient(main.app)


# --- fixtures ---

@pytest.fixture(autouse=True)
def fresh_db():
    """Recreate tables before each test so state doesn't leak."""
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(main.engine)
    SQLModel.metadata.create_all(main.engine)
    yield


# --- TODO 1: parametrize blank title validation ---

# @pytest.mark.parametrize(...)
def test_blank_titles_rejected():
    # TODO: parametrize over ["", "   ", "\t"]
    # each should raise ValidationError when passed to NoteCreate(title=...)
    raise NotImplementedError


# --- TODO 2: parametrize endpoint status codes ---

# @pytest.mark.parametrize(...)
def test_create_endpoint_payloads():
    # TODO: parametrize over (payload_dict, expected_status_code) pairs
    # include at least one valid case (201) and two invalid cases (422)
    raise NotImplementedError


# --- TODO 3: unknown fields rejected ---

def test_patch_rejects_unknown_fields():
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    # TODO: PATCH with an unknown field, assert 422
    raise NotImplementedError


# --- TODO 4: webhook called when URL is set ---

def test_notify_called_on_create(monkeypatch):
    monkeypatch.setattr(main, "WEBHOOK_URL", "http://test.example.com")
    # TODO: patch httpx.post (at "main.httpx.post"), create a note, assert mock was called
    raise NotImplementedError


# --- TODO 5: webhook not called when URL is empty ---

def test_notify_not_called_when_url_empty(monkeypatch):
    monkeypatch.setattr(main, "WEBHOOK_URL", "")
    # TODO: patch httpx.post, create a note, assert mock was NOT called
    raise NotImplementedError
