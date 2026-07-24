"""Exercise 3 — SOLUTION."""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine
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

# Also create tables at import time so the module-level TestClient in the tests works
# without entering the app's lifespan (TestClient only runs lifespan when used as a
# context manager). Harmless to call twice.
SQLModel.metadata.create_all(engine)


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(payload: NoteIn, session: Annotated[Session, Depends(get_session)]):
    note = Note(title=payload.title, done=payload.done)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.put("/notes/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    payload: NoteIn,
    session: Annotated[Session, Depends(get_session)],
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
