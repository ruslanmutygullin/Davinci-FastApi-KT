"""Tests for the request-data demo — all pass. Double as the spec.

Run: pytest test_request_data.py -v
"""

import io

from fastapi.testclient import TestClient

from request_data import app

client = TestClient(app)


def test_form_login():
    # `data=` sends form-encoded, not JSON.
    r = client.post("/login", data={"username": "ada", "password": "secret"})
    assert r.status_code == 200
    assert r.json() == {"user": "ada", "password_len": 6}


def test_form_missing_field_is_422():
    assert client.post("/login", data={"username": "ada"}).status_code == 422


def test_file_upload():
    files = {"file": ("hello.txt", io.BytesIO(b"hello world"), "text/plain")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "hello.txt"
    assert body["content_type"] == "text/plain"
    assert body["size"] == 11


def test_headers_and_cookies():
    r = client.get(
        "/whoami",
        headers={"User-Agent": "pytest-client"},
        cookies={"session_id": "abc123"},
    )
    body = r.json()
    assert body["user_agent"] == "pytest-client"
    assert body["session_id"] == "abc123"


def test_optional_header_and_cookie_default_to_none():
    r = client.get("/whoami")
    # both are optional; absent -> None
    assert r.json()["session_id"] is None
