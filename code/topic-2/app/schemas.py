"""API contract shapes, kept separate from the table model (models.py).

Separating these means storage can change without breaking the public API.
"""

from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    """What a client sends on create (and full-replace PUT) — no id (the DB assigns it)."""

    title: str
    done: bool = False


class NoteUpdate(SQLModel):
    """Partial update (PATCH) — every field optional so clients send only what changes.

    Combined with model_dump(exclude_unset=True) in the handler, an omitted field is left
    untouched rather than reset to a default.
    """

    title: str | None = None
    done: bool | None = None


class NoteRead(SQLModel):
    """What we send back — the safe, public fields."""

    id: int
    title: str
    done: bool
