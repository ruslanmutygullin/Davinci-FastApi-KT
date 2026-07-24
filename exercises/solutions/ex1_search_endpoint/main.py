"""Exercise 1 — SOLUTION."""

from fastapi import FastAPI
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


@app.get("/notes/search", response_model=list[Note])
async def search_notes(q: str):
    needle = q.lower()
    return [n for n in notes.values() if needle in n["title"].lower()]
