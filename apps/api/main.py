from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn

from auth import create_access_token, get_current_user, verify_password
from database import get_db
from init_db import init_database
from models import User, UserType
from routers import textbooks, users
from schemas import LoginRequest, LoginResponse, UserPublic


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_database()
    yield


app = FastAPI(title="Lingua API", lifespan=lifespan)
app.include_router(users.router)
app.include_router(textbooks.router)


def to_user_public(user: User) -> UserPublic:
    user_type = UserType(user.user_type)
    return UserPublic(
        id=user.id,
        username=user.username,
        user_type=user_type.value,
        user_type_description=user_type.description,
        created_at=user.created_at,
    )


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Lingua API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user_public = to_user_public(user)
    access_token = create_access_token(
        user_id=user_public.id,
        username=user_public.username,
        user_type=user_public.user_type,
    )
    return LoginResponse(access_token=access_token, user=user_public)


@app.get("/auth/me", response_model=UserPublic)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserPublic:
    return to_user_public(current_user)


def main() -> None:
    uvicorn.run("main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
