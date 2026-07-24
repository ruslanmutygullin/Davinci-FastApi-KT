"""Exercise 2 — SOLUTION."""

from typing import Annotated

from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

notes: dict[int, dict] = {}
_next_id = 1


class NoteCreate(BaseModel):
    title: str


class Note(NoteCreate):
    id: int
    owner: str


def get_current_user() -> str:
    return "demo-user"


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(
    payload: NoteCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    global _next_id
    note = {"id": _next_id, "title": payload.title, "owner": current_user}
    notes[_next_id] = note
    _next_id += 1
    return note
