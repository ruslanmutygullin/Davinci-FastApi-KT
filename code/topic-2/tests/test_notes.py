"""Reference tests for Topic 2 — all pass. Note there is no real notes.db involved;
conftest.py injects an in-memory database via dependency override.
"""


def test_create_and_read(client):
    created = client.post("/notes", json={"title": "Learn DI"})
    assert created.status_code == 201
    note_id = created.json()["id"]

    fetched = client.get(f"/notes/{note_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Learn DI"


def test_missing_note_404(client):
    assert client.get("/notes/999").status_code == 404


def test_list_notes(client):
    client.post("/notes", json={"title": "a"})
    client.post("/notes", json={"title": "b"})
    assert len(client.get("/notes").json()) == 2


def test_update(client):
    nid = client.post("/notes", json={"title": "old"}).json()["id"]
    r = client.put(f"/notes/{nid}", json={"title": "new", "done": True})
    assert r.status_code == 200
    assert r.json() == {"id": nid, "title": "new", "done": True}


def test_patch_only_changes_sent_fields(client):
    nid = client.post("/notes", json={"title": "keep me", "done": True}).json()["id"]

    # Send only `done` — `title` must be left untouched (that's the point of PATCH).
    r = client.patch(f"/notes/{nid}", json={"done": False})
    assert r.status_code == 200
    assert r.json() == {"id": nid, "title": "keep me", "done": False}


def test_delete_requires_api_key(client):
    nid = client.post("/notes", json={"title": "to delete"}).json()["id"]

    # Missing key -> 401 (guard is optional-with-check, so it's 401 not 422)
    assert client.delete(f"/notes/{nid}").status_code == 401
    # Wrong key -> 401
    assert client.delete(f"/notes/{nid}", headers={"x-api-key": "nope"}).status_code == 401
    # Correct key -> 204
    assert (
        client.delete(f"/notes/{nid}", headers={"x-api-key": "secret123"}).status_code
        == 204
    )
    # Now gone
    assert client.get(f"/notes/{nid}").status_code == 404
