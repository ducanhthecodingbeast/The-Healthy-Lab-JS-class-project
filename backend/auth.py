from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os

from fastapi import Depends, Header, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_session
from models import User


SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-for-production")
TOKEN_EXPIRE_HOURS = 12
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": (datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)).timestamp(),
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def read_token(token: str) -> dict:
    try:
        payload_b64, signature = token.split(".", 1)
        expected_signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError

        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
        if payload["exp"] < datetime.now(timezone.utc).timestamp():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    payload = read_token(authorization.replace("Bearer ", "", 1))
    user = session.get(User, payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User | None:
    if not authorization:
        return None
    return get_current_user(authorization=authorization, session=session)


def require_role(user: User | None, allowed_roles: list[str]):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission")
