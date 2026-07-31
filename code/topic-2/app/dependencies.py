from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.database import engine


def get_session():
    """Yield a per-request session; the `with` block closes it after the response.

    This is a dependency (see routers/notes.py). Everything before `yield` is setup,
    the yielded value is injected, and everything after `yield` is teardown.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
