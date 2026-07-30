"""Exercise 4 spec — passes against the solution."""

import io

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_contact_form():
    r = client.post("/contact", data={"name": "Grace", "email": "grace@example.com"})
    assert r.status_code == 200
    assert r.json() == {"name": "Grace", "email": "grace@example.com"}


def test_contact_requires_both_fields():
    assert client.post("/contact", data={"name": "Grace"}).status_code == 422


def test_avatar_upload():
    files = {"file": ("me.png", io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 20), "image/png")}
    r = client.post("/avatar", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "me.png"
    assert body["size"] == 28
