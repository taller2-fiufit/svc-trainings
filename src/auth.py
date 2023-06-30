import os
from typing import Annotated, Optional
from http import HTTPStatus
from pydantic import BaseModel
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request, Response

from src.logging import info

_AUTH_SECRET = os.getenv("AUTH_SECRET")
AUTH_SECRET = _AUTH_SECRET if _AUTH_SECRET is not None else ""

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="https://svc-users-fedecolangelo.cloud.okteto.net/tokens",
)


class User(BaseModel):
    email: str
    sub: int
    admin: bool


async def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Validates token and extracts user information"""
    try:
        user_info = jwt.decode(
            token,
            AUTH_SECRET,
            algorithms="HS256",
            options={"verify_sub": False},
        )
    except (JWTError, ExpiredSignatureError, JWTClaimsError):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "Token is invalid or has expired"
        )

    return User(**user_info)


async def get_admin(user: Annotated[User, Depends(get_user)]) -> User:
    """Validates that the user is an admin, and returns the user"""
    if not user.admin:
        raise HTTPException(
            HTTPStatus.FORBIDDEN, "Action requires admin permissions"
        )
    return user


DUMMY_ADMIN = User(email="dummy@example.com", sub=1, admin=True)


async def ignore_auth() -> User:
    """Used for tests without authentication"""
    return DUMMY_ADMIN


APIKEY = os.getenv("APIKEY")
APIKEY_HEADER = "X-Apikey"


def req_apikey_is_valid(apikey: Optional[str]) -> bool:
    """Returns True if the apikey is valid or we aren't checking"""
    if APIKEY is not None and apikey != APIKEY:
        info(f"Invalid APIkey received: {apikey}")
        return False
    return True


class ApikeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        apikey = request.headers.get(APIKEY_HEADER, None)

        if request.url.path != "/health" and not req_apikey_is_valid(apikey):
            return Response(status_code=HTTPStatus.UNAUTHORIZED)

        return await call_next(request)
