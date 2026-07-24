"""Exercise 3 — a health check and a DB-backed update.

GOAL:
  1. Add `GET /health` returning {"status": "ok"} (status 200).
  2. Add `PUT /notes/{note_id}` that updates a note in the database and returns it,
     or 404 if it doesn't exist.

The app is a small self-contained SQLModel app (in-memory DB for simplicity). See
test_ex3.py for the spec. Run `pytest -v`, then complete the TODOs.
"""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlmodel.pool import StaticPool

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False


class NoteIn(SQLModel):
    title: str
    done: bool = False


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

# Also create tables at import time so the tests' module-level TestClient works without
# entering the lifespan. Harmless to call twice. (Leave this line as-is.)
SQLModel.metadata.create_all(engine)


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(payload: NoteIn, session: Annotated[Session, Depends(get_session)]):
    note = Note(title=payload.title, done=payload.done)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


# TODO 1: add GET /health that returns {"status": "ok"}.


# TODO 2: add PUT /notes/{note_id}:
#   - load the note with session.get(Note, note_id)
#   - if missing, raise HTTPException(status_code=404, detail="Note not found")
#   - otherwise update title & done from the payload, commit, refresh, and return it
#   - use response_model=Note
