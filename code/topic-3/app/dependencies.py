from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.auth import get_current_user
from app.database import engine


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[str, Depends(get_current_user)]
