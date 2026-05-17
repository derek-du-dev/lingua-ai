from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth import get_password_hash, require_admin
from database import get_db
from models import User, UserType
from schemas import ResetPasswordResponse, UserCreate, UserPublic, UserUpdate
from system_settings import get_system_settings

router = APIRouter(prefix="/users", tags=["users"])


def to_user_public(user: User) -> UserPublic:
    user_type = UserType(user.user_type)
    return UserPublic(
        id=user.id,
        username=user.username,
        user_type=user_type.value,
        user_type_description=user_type.description,
        created_at=user.created_at,
    )


def get_valid_user_type(user_type: int) -> UserType:
    try:
        return UserType(user_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的用户类型") from exc


def get_user_or_404(user_id: str, db: Session) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


def ensure_username_available(username: str, db: Session, exclude_user_id: Optional[str] = None) -> None:
    existing = db.query(User).filter(User.username == username).first()
    if existing is not None and existing.id != exclude_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")


@router.get("/", response_model=list[UserPublic], status_code=status.HTTP_200_OK, include_in_schema=False)
@router.get("", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[UserPublic]:
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [to_user_public(user) for user in users]


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> UserPublic:
    user_type = get_valid_user_type(payload.user_type)
    ensure_username_available(payload.username, db)

    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        user_type=user_type.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_user_public(user)


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> UserPublic:
    user = get_user_or_404(user_id, db)
    user_type = get_valid_user_type(payload.user_type)

    if user.username == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内置管理员不能修改")
    if payload.username == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能使用内置管理员用户名")

    ensure_username_available(payload.username, db, exclude_user_id=user.id)

    user.username = payload.username
    user.user_type = user_type.value
    db.commit()
    db.refresh(user)
    return to_user_public(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Response:
    user = get_user_or_404(user_id, db)

    if user.username == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内置管理员不能删除")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录用户")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{user_id}/reset-password", response_model=ResetPasswordResponse)
def reset_user_password(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> ResetPasswordResponse:
    user = get_user_or_404(user_id, db)

    if user.username == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内置管理员不能重置密码")

    default_password = get_system_settings().default_password
    user.password_hash = get_password_hash(default_password)
    db.commit()
    return ResetPasswordResponse(message=f"密码已重置为 {default_password}")
