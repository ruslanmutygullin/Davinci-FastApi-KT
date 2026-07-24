"""Authentication as a dependency.

OAuth2PasswordBearer pulls the token from the `Authorization: Bearer <token>` header and
wires up the /docs "Authorize" button. get_current_user decodes it. Because it's a
dependency, any route can require a user just by asking for one — and tests can override it.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(subject: str) -> str:
    """Issue a signed JWT for a user (used by the /token login route)."""
    return jwt.encode({"sub": subject}, settings.jwt_secret, algorithm="HS256")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]
