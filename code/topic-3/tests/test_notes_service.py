"""Direct service tests — no HTTP, no TestClient.

Calling service functions with a real (in-memory) DB session is faster than
going through the HTTP stack and tests the logic in isolation. Use this style
for business-rule tests; use test_notes_router.py for HTTP contract tests.
"""

import pytest

from app.errors import NoteNotFoundError
from app.schemas import NoteCreate, NoteUpdate
from app.services.notes import note_service


def test_create_persists_note(db):
    note = note_service.create(db, NoteCreate(title="hello"))
    assert note.id is not None
    assert note.title == "hello"
    assert note.done is False


def test_create_strips_whitespace(db):
    note = note_service.create(db, NoteCreate(title="  trimmed  "))
    assert note.title == "trimmed"


def test_get_returns_note(db):
    created = note_service.create(db, NoteCreate(title="find me"))
    fetched = note_service.get(db, created.id)
    assert fetched.id == created.id


def test_get_raises_for_missing(db):
    with pytest.raises(NoteNotFoundError):
        note_service.get(db, 999)


def test_patch_applies_partial_update(db):
    note = note_service.create(db, NoteCreate(title="original"))
    patched = note_service.patch(db, note.id, NoteUpdate(done=True))
    assert patched.title == "original"   # unchanged
    assert patched.done is True


def test_delete_removes_note(db):
    note = note_service.create(db, NoteCreate(title="temp"))
    note_service.delete(db, note.id)
    with pytest.raises(NoteNotFoundError):
        note_service.get(db, note.id)


def test_get_all_filters_by_done(db):
    note_service.create(db, NoteCreate(title="pending"))
    note_service.create(db, NoteCreate(title="done", done=True))
    done = note_service.get_all(db, done=True)
    assert all(n.done for n in done)
    assert len(done) == 1


def test_get_all_searches_title(db):
    note_service.create(db, NoteCreate(title="meeting notes"))
    note_service.create(db, NoteCreate(title="grocery list"))
    results = note_service.get_all(db, search="meeting")
    assert len(results) == 1
    assert results[0].title == "meeting notes"


def test_get_all_paginates(db):
    for i in range(5):
        note_service.create(db, NoteCreate(title=f"note {i}"))
    page1 = note_service.get_all(db, page=1, size=3)
    page2 = note_service.get_all(db, page=2, size=3)
    assert len(page1) == 3
    assert len(page2) == 2
    assert {n.id for n in page1}.isdisjoint({n.id for n in page2})
