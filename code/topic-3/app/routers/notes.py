"""Notes endpoints for Topic 3.

New vs Topic 2:
- reads require a logged-in user (Depends(get_current_user)) — auth is just a dependency.
- get_note raises the domain NoteNotFoundError instead of HTTPException directly.
- a /token login route issues a JWT so you can try the protected routes.
"""

from fastapi import APIRouter, Depends
from sqlmodel import select

from app.auth import create_access_token
from app.dependencies import SessionDep, CurrentUserDep, require_api_key
from app.errors import NoteNotFoundError
from app.models import Note
from app.schemas import NoteCreate, NoteRead

router = APIRouter(tags=["notes"])


@router.post("/token")
async def login():
    """A stand-in login. A real one verifies a username/password first.

    Returns a bearer token you can paste into the /docs "Authorize" dialog.
    """
    return {"access_token": create_access_token("demo-user"), "token_type": "bearer"}


@router.get("/notes", response_model=list[NoteRead])
async def list_notes(session: SessionDep, current_user: CurrentUserDep):
    return session.exec(select(Note)).all()


@router.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(payload: NoteCreate, session: SessionDep, current_user: CurrentUserDep):
    note = Note(title=payload.title, done=payload.done)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, session: SessionDep, current_user: CurrentUserDep):
    note = session.get(Note, note_id)
    if not note:
        raise NoteNotFoundError(note_id)  # handled centrally in main.py
    return note


@router.delete("/notes/{note_id}", status_code=204, dependencies=[Depends(require_api_key)])
async def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise NoteNotFoundError(note_id)
    session.delete(note)
    session.commit()
