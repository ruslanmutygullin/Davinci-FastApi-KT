from typing import Annotated

from fastapi import Depends, HTTPException, Header
from sqlmodel import Session

from app.auth import get_current_user
from app.config import settings
from app.database import engine


def get_session():
    with Session(engine) as session:
        yield session


def require_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[str, Depends(get_current_user)]
