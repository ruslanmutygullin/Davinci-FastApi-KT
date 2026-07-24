"""Topic 1 — a single-file Notes API.

Everything lives here on purpose: routes, Pydantic models, and an in-memory "database"
(a plain dict). Data resets every time the server restarts — that's fine for learning the
request/validation/response cycle. Topic 2 replaces the dict with a real database.

Run it:   uvicorn main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Our "database" for now — just a dict in memory.
notes: dict[int, dict] = {}
_next_id = 1


class NoteCreate(BaseModel):
    """Request body: what a client sends to create/update a note."""

    title: str
    done: bool = False


class Note(NoteCreate):
    """Response shape: NoteCreate plus the server-assigned id."""

    id: int


@app.get("/notes", response_model=list[Note])
async def list_notes(done: bool | None = None):
    # `done` is an optional query param: /notes?done=true
    if done is None:
        return list(notes.values())
    return [n for n in notes.values() if n["done"] == done]


@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(payload: NoteCreate):
    global _next_id
    note = {"id": _next_id, "title": payload.title, "done": payload.done}
    notes[_next_id] = note
    _next_id += 1
    return note


@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, payload: NoteCreate):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    notes[note_id].update(title=payload.title, done=payload.done)
    return notes[note_id]


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]
