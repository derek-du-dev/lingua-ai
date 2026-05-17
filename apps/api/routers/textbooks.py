from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth import require_admin
from database import get_db
from models import Textbook, User
from schemas import TextbookCreate, TextbookPublic, TextbookUpdate

router = APIRouter(prefix="/textbooks", tags=["textbooks"])


def to_textbook_public(textbook: Textbook) -> TextbookPublic:
    return TextbookPublic(id=textbook.id, name=textbook.name)


def get_textbook_or_404(textbook_id: str, db: Session) -> Textbook:
    textbook = db.get(Textbook, textbook_id)
    if textbook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教材不存在")
    return textbook


def ensure_textbook_name_available(name: str, db: Session, exclude_textbook_id: Optional[str] = None) -> None:
    existing = db.query(Textbook).filter(Textbook.name == name).first()
    if existing is not None and existing.id != exclude_textbook_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="教材名称已存在")


@router.get("/", response_model=list[TextbookPublic], status_code=status.HTTP_200_OK, include_in_schema=False)
@router.get("", response_model=list[TextbookPublic], status_code=status.HTTP_200_OK)
def list_textbooks(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[TextbookPublic]:
    textbooks = db.query(Textbook).order_by(Textbook.name.asc()).all()
    return [to_textbook_public(textbook) for textbook in textbooks]


@router.post("", response_model=TextbookPublic, status_code=status.HTTP_201_CREATED)
def create_textbook(
    payload: TextbookCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> TextbookPublic:
    ensure_textbook_name_available(payload.name, db)

    textbook = Textbook(name=payload.name)
    db.add(textbook)
    db.commit()
    db.refresh(textbook)
    return to_textbook_public(textbook)


@router.put("/{textbook_id}", response_model=TextbookPublic)
def update_textbook(
    textbook_id: str,
    payload: TextbookUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> TextbookPublic:
    textbook = get_textbook_or_404(textbook_id, db)
    ensure_textbook_name_available(payload.name, db, exclude_textbook_id=textbook.id)

    textbook.name = payload.name
    db.commit()
    db.refresh(textbook)
    return to_textbook_public(textbook)


@router.delete("/{textbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_textbook(
    textbook_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    textbook = get_textbook_or_404(textbook_id, db)
    db.delete(textbook)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
