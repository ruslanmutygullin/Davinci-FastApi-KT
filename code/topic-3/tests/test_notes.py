"""Reference tests for Topic 3 — all pass.

`client` fakes the logged-in user (auth overridden). `real_auth_client` exercises the
genuine JWT flow (login -> use token).
"""


def test_create_and_read_with_fake_auth(client):
    created = client.post("/notes", json={"title": "prod-ready"})
    assert created.status_code == 201
    nid = created.json()["id"]

    fetched = client.get(f"/notes/{nid}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "prod-ready"


def test_missing_note_uses_custom_error_shape(client):
    r = client.get("/notes/999")
    assert r.status_code == 404
    # The centralized handler produces {"error": ...}, not the default {"detail": ...}
    assert r.json() == {"error": "Note 999 does not exist"}


def test_delete_requires_api_key(client):
    nid = client.post("/notes", json={"title": "x"}).json()["id"]
    assert client.delete(f"/notes/{nid}").status_code == 401
    assert (
        client.delete(f"/notes/{nid}", headers={"x-api-key": "secret123"}).status_code
        == 204
    )


def test_protected_route_rejects_anonymous(real_auth_client):
    # No token at all -> 401 from OAuth2PasswordBearer
    assert real_auth_client.get("/notes").status_code == 401


def test_protected_route_rejects_bad_token(real_auth_client):
    r = real_auth_client.get("/notes", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


def test_real_jwt_login_flow(real_auth_client):
    token = real_auth_client.post("/token").json()["access_token"]
    r = real_auth_client.get("/notes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_cors_header_present(client):
    r = client.get(
        "/notes", headers={"Origin": "http://localhost:5173"}
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
