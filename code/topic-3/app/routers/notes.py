"""Notes router — thin HTTP layer.

Each handler does three things only: declare what it needs (deps + params),
call the service, return the result. No business logic lives here.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth import create_access_token
from app.dependencies import CurrentUserDep, SessionDep, require_api_key
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.services.notes import note_service

router = APIRouter(tags=["notes"])


@router.post("/token")
async def login():
    """Stand-in login — returns a JWT for the demo user.

    A real login would verify a username/password first.
    """
    return {"access_token": create_access_token("demo-user"), "token_type": "bearer"}


@router.get("/notes", response_model=list[NoteRead])
async def list_notes(
    session: SessionDep,
    current_user: CurrentUserDep,
    done: bool | None = None,
    search: str | None = None,
    page: int = 1,
    size: int = 20,
):
    return note_service.get_all(session, done=done, search=search, page=page, size=size)


@router.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(payload: NoteCreate, session: SessionDep, current_user: CurrentUserDep):
    return note_service.create(session, payload)


@router.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, session: SessionDep, current_user: CurrentUserDep):
    return note_service.get(session, note_id)


@router.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(note_id: int, payload: NoteCreate, session: SessionDep, current_user: CurrentUserDep):
    return note_service.update(session, note_id, payload)


@router.patch("/notes/{note_id}", response_model=NoteRead)
async def patch_note(note_id: int, payload: NoteUpdate, session: SessionDep, current_user: CurrentUserDep):
    return note_service.patch(session, note_id, payload)


@router.delete("/notes/{note_id}", status_code=204, dependencies=[Depends(require_api_key)])
async def delete_note(note_id: int, session: SessionDep):
    note_service.delete(session, note_id)
