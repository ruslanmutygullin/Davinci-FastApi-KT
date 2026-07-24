"""Tests for the serialization demo — all pass. They show exactly what each Python type
becomes in the JSON response.
"""

from fastapi.testclient import TestClient

from serialization import app

client = TestClient(app)


def test_types_serialize_to_json_friendly_values():
    body = client.get("/invoice").json()

    # UUID -> string
    assert body["id"] == "12345678-1234-5678-1234-567812345678"
    # datetime -> ISO 8601 string
    assert body["created_at"].startswith("2026-07-24T12:30:00")
    # Decimal -> JSON STRING (Pydantic v2 preserves exact precision, so NOT a float)
    assert body["amount"] == "19.99"
    # Enum -> its value
    assert body["currency"] == "USD"
    # set -> list
    assert body["tags"] == ["paid"]
