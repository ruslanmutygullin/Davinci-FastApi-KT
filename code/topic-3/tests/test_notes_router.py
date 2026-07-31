"""Router-level integration tests — exercises the full HTTP stack via TestClient.

The `client` fixture (conftest.py) fakes auth so these tests focus on the
HTTP contract, not the token flow. See test_notes_service.py for pure logic tests.
"""

from unittest.mock import patch

from app.config import settings


def test_create_and_read(client):
    created = client.post("/notes", json={"title": "buy oat milk"})
    assert created.status_code == 201
    nid = created.json()["id"]

    fetched = client.get(f"/notes/{nid}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "buy oat milk"


def test_list_notes(client):
    client.post("/notes", json={"title": "a"})
    client.post("/notes", json={"title": "b"})
    r = client.get("/notes")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_list_filter_by_done(client):
    client.post("/notes", json={"title": "pending", "done": False})
    client.post("/notes", json={"title": "finished", "done": True})
    done = client.get("/notes?done=true").json()
    assert all(n["done"] for n in done)


def test_list_search(client):
    client.post("/notes", json={"title": "meeting notes"})
    client.post("/notes", json={"title": "grocery list"})
    results = client.get("/notes?search=meeting").json()
    assert len(results) == 1
    assert results[0]["title"] == "meeting notes"


def test_missing_note_uses_custom_error_shape(client):
    r = client.get("/notes/999")
    assert r.status_code == 404
    # Centralized handler produces {"error": ...}, not the default {"detail": ...}
    assert r.json() == {"error": "Note 999 does not exist"}


def test_delete_requires_api_key(client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    assert client.delete(f"/notes/{nid}").status_code == 401
    assert client.delete(f"/notes/{nid}", headers={"x-api-key": settings.api_key}).status_code == 204


def test_protected_route_rejects_anonymous(real_auth_client):
    assert real_auth_client.get("/notes").status_code == 401


def test_protected_route_rejects_bad_token(real_auth_client):
    r = real_auth_client.get("/notes", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


def test_real_jwt_login_flow(real_auth_client):
    token = real_auth_client.post("/token").json()["access_token"]
    r = real_auth_client.get("/notes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_cors_header_present(client):
    r = client.get("/notes", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_create_calls_webhook(client):
    """patch() intercepts httpx.post inside the service — real HTTP never fires.

    This is the canonical mocking pattern: patch where the name is *used*
    (app.services.notes.httpx.post), not where it's defined (httpx.post).
    """
    with patch("app.services.notes.httpx.post") as mock_post:
        r = client.post("/notes", json={"title": "webhook test"})
        assert r.status_code == 201
        # webhook_url is empty in test config, so _notify() returns early
        mock_post.assert_not_called()


def test_patch_rejects_unknown_fields(client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    r = client.patch(f"/notes/{nid}", json={"titl": "typo"})  # typo field
    assert r.status_code == 422


def test_patch_requires_at_least_one_field(client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    r = client.patch(f"/notes/{nid}", json={})
    assert r.status_code == 422
