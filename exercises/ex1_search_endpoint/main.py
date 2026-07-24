"""Exercise 1 — add a search endpoint.

GOAL: implement `GET /notes/search?q=<term>` that returns only the notes whose title
contains `q` (case-insensitive). See test_ex1.py for the exact spec.

Run `pytest -v` to see the failing test, then make it pass by completing the TODO.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

notes: dict[int, dict] = {}
_next_id = 1


class NoteCreate(BaseModel):
    title: str
    done: bool = False


class Note(NoteCreate):
    id: int


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(payload: NoteCreate):
    global _next_id
    note = {"id": _next_id, "title": payload.title, "done": payload.done}
    notes[_next_id] = note
    _next_id += 1
    return note


# TODO: add a GET /notes/search endpoint.
#   - It takes a required query parameter `q: str`.
#   - It returns a list of notes whose `title` CONTAINS `q`, case-insensitively.
#   - Use response_model=list[Note].
#
# Hint: FastAPI reads `q` from the query string because it's a bare scalar not in the path.
# Remember to register the route ABOVE any `/notes/{note_id}` route so "search" isn't
# mistaken for an id (not an issue here, but good habit).
