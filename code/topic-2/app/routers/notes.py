"""Notes endpoints. Every DB-touching route gets its session via Depends(get_session).

Because the session is *injected* rather than imported, tests can swap it for a throwaway
database with app.dependency_overrides (see tests/conftest.py) — the whole reason for DI.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import select

from app.dependencies import SessionDep
from app.models import Note
from app.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def require_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """A guard dependency. Kept optional so WE choose the status code.

    If this were a *required* header, a missing header would fail validation with a 422
    before this function runs. Making it optional lets us return 401 for both missing and
    wrong keys.
    """
    if x_api_key != "secret123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.get("", response_model=list[NoteRead])
async def list_notes(session: SessionDep):
    return session.exec(select(Note)).all()


@router.post("", response_model=NoteRead, status_code=201)
async def create_note(
    payload: NoteCreate,
    session: SessionDep,
):
    note = Note(title=payload.title, done=payload.done)
    session.add(note)
    session.commit()
    session.refresh(note)  # reload so note.id (assigned by the DB) is populated
    return note


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: int,
    payload: NoteCreate,
    session: SessionDep,
):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = payload.title
    note.done = payload.done
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.patch("/{note_id}", response_model=NoteRead)
async def patch_note(
    note_id: int,
    payload: NoteUpdate,
    session: SessionDep,
):
    """Partial update: apply only the fields the client actually sent.

    exclude_unset=True is the crux — it distinguishes an omitted field from one explicitly
    set, so we never overwrite data the client didn't touch (contrast the PUT above, which
    replaces every field).
    """
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204, dependencies=[Depends(require_api_key)])
async def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
