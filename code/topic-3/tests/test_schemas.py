"""Schema / validator tests using pytest.mark.parametrize.

parametrize runs one test function against multiple inputs — the same idea as
Jest's test.each. Use it whenever you have the same assertion over a range of
values: invalid inputs, boundary conditions, valid variations.
"""

import pytest
from pydantic import ValidationError

from app.schemas import NoteCreate, NoteUpdate


# --- NoteCreate ---

@pytest.mark.parametrize("title", ["", "   ", "\t", "\n"])
def test_blank_title_rejected(title):
    with pytest.raises(ValidationError):
        NoteCreate(title=title)


@pytest.mark.parametrize("title,expected", [
    ("  hello  ", "hello"),
    ("no padding", "no padding"),
    (" leading", "leading"),
    ("trailing ", "trailing"),
])
def test_title_whitespace_stripped(title, expected):
    note = NoteCreate(title=title)
    assert note.title == expected


# --- NoteUpdate ---

def test_update_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        NoteUpdate(titl="typo")   # extra="forbid" catches this


def test_update_requires_at_least_one_field():
    with pytest.raises(ValidationError):
        NoteUpdate()


@pytest.mark.parametrize("payload", [
    {"title": "new title"},
    {"done": True},
    {"title": "new", "done": False},
])
def test_update_valid_payloads(payload):
    update = NoteUpdate(**payload)
    assert update is not None


@pytest.mark.parametrize("payload,expected_status", [
    ({"title": "valid"}, 201),
    ({"title": ""}, 422),
    ({"title": "   "}, 422),
    ({"title": "ok", "done": True}, 201),
])
def test_create_endpoint_validation(client, payload, expected_status):
    r = client.post("/notes", json=payload)
    assert r.status_code == expected_status
