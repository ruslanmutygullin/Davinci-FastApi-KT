"""API contract shapes, kept separate from the table model (models.py).

Separating these means storage can change without breaking the public API.
"""

from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    """What a client sends — no id (the DB assigns it)."""

    title: str
    done: bool = False


class NoteRead(SQLModel):
    """What we send back — the safe, public fields."""

    id: int
    title: str
    done: bool
