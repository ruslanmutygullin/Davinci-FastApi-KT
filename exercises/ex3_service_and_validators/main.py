"""Exercise 3 — service layer and validators.

GOAL: refactor the notes app below to introduce a service layer and input validation.

  1. Create a `NoteService` class in this file with:
       - `get(db, note_id)` — returns the note or raises `NoteNotFoundError`
       - `create(db, payload)` — creates and returns a note
       - `patch(db, note_id, payload)` — partial update using model_dump(exclude_unset=True)

  2. Add a `@field_validator("title")` on `NoteCreate` that:
       - rejects blank/whitespace-only titles (raise ValueError)
       - strips surrounding whitespace from valid titles

  3. Add `extra="forbid"` and a `@model_validator` on `NoteUpdate` that:
       - rejects unknown fields
       - rejects a payload where both fields are None (empty PATCH)

  4. Make the router handlers delegate to `note_service` — no business logic in the router.

Run `pytest -v` to see the failing tests, then make them pass.
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlmodel.pool import StaticPool

# --- DB setup (leave as-is) ---

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)
SQLModel.metadata.create_all(engine)  # also at import time for tests


# --- Domain exception (leave as-is) ---

class NoteNotFoundError(Exception):
    def __init__(self, note_id: int):
        self.note_id = note_id


@app.exception_handler(NoteNotFoundError)
async def note_not_found_handler(request: Request, exc: NoteNotFoundError):
    return JSONResponse(status_code=404, content={"error": f"Note {exc.note_id} does not exist"})


# --- Model (leave as-is) ---

class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False


# --- Schemas: TODO add validators ---

class NoteCreate(SQLModel):
    title: str
    done: bool = False

    # TODO: add @field_validator("title") that rejects blank titles and strips whitespace


class NoteUpdate(SQLModel):
    # TODO: add model_config = ConfigDict(extra="forbid")
    title: str | None = None
    done: bool | None = None

    # TODO: add @model_validator(mode="after") that rejects empty payloads


# --- Service: TODO implement ---

class NoteService:
    def get(self, db: Session, note_id: int) -> Note:
        # TODO: look up the note; raise NoteNotFoundError if missing
        raise NotImplementedError

    def create(self, db: Session, payload: NoteCreate) -> Note:
        # TODO: create, add, commit, refresh, return
        raise NotImplementedError

    def patch(self, db: Session, note_id: int, payload: NoteUpdate) -> Note:
        # TODO: get the note, apply model_dump(exclude_unset=True), commit, return
        raise NotImplementedError


note_service = NoteService()


# --- Router: TODO delegate to note_service ---

class NoteRead(SQLModel):
    id: int
    title: str
    done: bool


@app.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(payload: NoteCreate, session: SessionDep):
    # TODO: call note_service.create
    raise NotImplementedError


@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, session: SessionDep):
    # TODO: call note_service.get
    raise NotImplementedError


@app.patch("/notes/{note_id}", response_model=NoteRead)
async def patch_note(note_id: int, payload: NoteUpdate, session: SessionDep):
    # TODO: call note_service.patch
    raise NotImplementedError
