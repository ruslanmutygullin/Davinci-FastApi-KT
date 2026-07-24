"""Exercise 2 — inject a value with a dependency.

GOAL: create a dependency `get_current_user` that returns the string "demo-user", and
inject it into `create_note` so each created note records its `owner`. See test_ex2.py.

This is single-file to keep the focus on the dependency-injection mechanic from Topic 2.
Run `pytest -v`, read the failing test, then complete the TODOs.
"""

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


# TODO 1: write a dependency function `get_current_user` that returns "demo-user".
#         (In a real app it would decode a token — here just return the string.)


# TODO 2: inject it into create_note below via `Depends(get_current_user)` and store the
#         returned value as the note's `owner`.
@app.post("/notes", response_model=Note, status_code=201)
async def create_note(payload: NoteCreate):
    global _next_id
    note = {
        "id": _next_id,
        "title": payload.title,
        "owner": "TODO-replace-me",  # <- should come from the injected current user
    }
    notes[_next_id] = note
    _next_id += 1
    return note
