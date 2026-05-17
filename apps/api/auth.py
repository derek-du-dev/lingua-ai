import os
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import DATA_DIR, get_db
from models import User, UserType

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_FILE = DATA_DIR / ".jwt_secret"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_jwt_secret() -> str:
    env_secret = os.getenv("LINGUA_JWT_SECRET")
    if env_secret:
        return env_secret

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()

    secret = token_urlsafe(32)
    SECRET_FILE.write_text(secret, encoding="utf-8")
    return secret


def create_access_token(user_id: str, username: str, user_type: int) -> str:
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
        "user_type": user_type,
        "exp": expires_at,
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise auth_error

    try:
        payload = jwt.decode(credentials.credentials, get_jwt_secret(), algorithms=[ALGORITHM])
    except JWTError as exc:
        raise auth_error from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise auth_error

    user = db.get(User, user_id)
    if user is None:
        raise auth_error

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    try:
        user_type = UserType(current_user.user_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required") from exc

    if user_type != UserType.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")

    return current_user


def require_teacher_or_admin(current_user: User = Depends(get_current_user)) -> User:
    try:
        user_type = UserType(current_user.user_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Management permission required") from exc

    if user_type not in {UserType.TEACHER, UserType.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Management permission required")

    return current_user
