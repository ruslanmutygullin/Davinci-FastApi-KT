"""Spec for Exercise 1. These FAIL against the starter and PASS once you add the endpoint."""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_store():
    main.notes.clear()
    main._next_id = 1
    yield


client = TestClient(main.app)


def seed():
    for title in ["Buy milk", "Buy bread", "Learn FastAPI"]:
        client.post("/notes", json={"title": title})


def test_search_matches_substring_case_insensitive():
    seed()
    r = client.get("/notes/search", params={"q": "buy"})
    assert r.status_code == 200
    titles = sorted(n["title"] for n in r.json())
    assert titles == ["Buy bread", "Buy milk"]


def test_search_returns_empty_when_no_match():
    seed()
    r = client.get("/notes/search", params={"q": "zzz"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_requires_q():
    # q is a required query param -> missing it is a 422
    assert client.get("/notes/search").status_code == 422
