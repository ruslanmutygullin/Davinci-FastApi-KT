"""Tests for the advanced-models demo — all pass. They double as the spec for what each
validation rule does. Run `pytest test_advanced_models.py -v`.
"""

from fastapi.testclient import TestClient

from advanced_models import app

client = TestClient(app)


def test_minimal_valid_task():
    r = client.post("/tasks", json={"title": "Write docs"})
    assert r.status_code == 200
    body = r.json()
    assert body["priority"] == "medium"   # default applied
    assert body["due_days"] is None       # optional, defaulted to null
    assert body["tags"] == []


def test_title_is_trimmed_by_validator():
    r = client.post("/tasks", json={"title": "  spaced  "})
    assert r.json()["title"] == "spaced"  # field_validator normalized it


def test_blank_title_rejected():
    # whitespace-only -> validator raises -> 422
    assert client.post("/tasks", json={"title": "   "}).status_code == 422


def test_title_too_long_rejected():
    assert client.post("/tasks", json={"title": "x" * 201}).status_code == 422


def test_enum_validation():
    ok = client.post("/tasks", json={"title": "t", "priority": "low"})
    assert ok.json()["priority"] == "low"
    # not a member of the enum -> 422
    assert client.post("/tasks", json={"title": "t", "priority": "urgent"}).status_code == 422


def test_due_days_constraint():
    # le=365 -> 400 is out of range
    assert client.post("/tasks", json={"title": "t", "due_days": 400}).status_code == 422
    # ge=0 -> negative is out of range
    assert client.post("/tasks", json={"title": "t", "due_days": -1}).status_code == 422


def test_nested_tags_validated():
    ok = client.post("/tasks", json={"title": "t", "tags": [{"name": "work"}]})
    assert ok.status_code == 200
    assert ok.json()["tags"][0]["name"] == "work"
    # nested Tag.name has min_length=1 -> empty name is rejected
    bad = client.post("/tasks", json={"title": "t", "tags": [{"name": ""}]})
    assert bad.status_code == 422


def test_model_validator_cross_field_rule():
    # high priority without due_days -> model_validator rejects -> 422
    bad = client.post("/tasks", json={"title": "t", "priority": "high"})
    assert bad.status_code == 422
    # high priority WITH due_days -> ok
    ok = client.post("/tasks", json={"title": "t", "priority": "high", "due_days": 7})
    assert ok.status_code == 200
