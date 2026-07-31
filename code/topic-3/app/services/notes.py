"""Business logic for notes — no HTTP, no FastAPI imports.

The service receives a DB session injected by the router. It raises domain
exceptions (NoteNotFoundError) that the centralized handler in main.py converts
to HTTP responses. This keeps the service layer HTTP-agnostic and directly testable.

The _notify() helper demonstrates the pattern of an external side-effect call (a
webhook, an email, a Coveo sync). Because it's a plain function call inside the
service, tests can patch it with unittest.mock.patch without touching app code.
"""

import httpx
from sqlmodel import Session, select

from app.config import settings
from app.errors import NoteNotFoundError
from app.models import Note
from app.schemas import NoteCreate, NoteUpdate


def _notify(note: Note) -> None:
    """Best-effort webhook call — failures are swallowed, never break the request."""
    if not settings.webhook_url:
        return
    try:
        httpx.post(settings.webhook_url, json={"id": note.id, "title": note.title}, timeout=5)
    except Exception:  # noqa: BLE001
        pass


class NoteService:
    @staticmethod
    def get_all(
        db: Session,
        *,
        done: bool | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Note]:
        stmt = select(Note).order_by(Note.id)  # type: ignore[arg-type]
        if done is not None:
            stmt = stmt.where(Note.done == done)
        if search:
            stmt = stmt.where(Note.title.contains(search))  # type: ignore[attr-defined]
        stmt = stmt.offset((page - 1) * size).limit(size)
        return list(db.exec(stmt).all())  # type: ignore[arg-type]

    @staticmethod
    def get(db: Session, note_id: int) -> Note:
        note: Note | None = db.get(Note, note_id)  # type: ignore[assignment]
        if not note:
            raise NoteNotFoundError(note_id)
        return note

    @staticmethod
    def create(db: Session, payload: NoteCreate) -> Note:
        note = Note(title=payload.title, done=payload.done)
        db.add(note)
        db.commit()
        db.refresh(note)
        _notify(note)
        return note

    def update(self, db: Session, note_id: int, payload: NoteCreate) -> Note:
        note = self.get(db, note_id)
        note.title = payload.title
        note.done = payload.done
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    def patch(self, db: Session, note_id: int, payload: NoteUpdate) -> Note:
        note = self.get(db, note_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(note, key, value)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    def delete(self, db: Session, note_id: int) -> None:
        note = self.get(db, note_id)
        db.delete(note)
        db.commit()


note_service = NoteService()
