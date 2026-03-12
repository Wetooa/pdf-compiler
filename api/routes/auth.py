"""Simple password auth: login and JWT verification."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel

from src.config import Config

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


class LoginBody(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


def _make_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": "user", "exp": now + timedelta(hours=JWT_EXPIRY_HOURS), "iat": now}
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=JWT_ALGORITHM)


def _verify_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def require_auth(authorization: str | None = Header(None)) -> dict[str, Any]:
    """Dependency: require valid Bearer token; raise 401 if missing or invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    return _verify_token(token)


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginBody):
    """Check password and return JWT. Single shared password from APP_PASSWORD."""
    expected = Config.APP_PASSWORD
    if not expected:
        raise HTTPException(status_code=503, detail="Authentication not configured (APP_PASSWORD unset)")
    if not secrets.compare_digest(body.password.encode("utf-8"), expected.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid password")
    return LoginResponse(token=_make_token())


@router.get("/me")
async def me(_: dict[str, Any] = Depends(require_auth)):
    """Confirm token is valid. Returns 200 with ok."""
    return {"ok": True}
