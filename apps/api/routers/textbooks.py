from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth import require_teacher_or_admin
from database import get_db
from models import Article, Textbook, User
from schemas import ArticleCreate, ArticlePublic, TextbookCreate, TextbookPublic, TextbookUpdate

router = APIRouter(prefix="/textbooks", tags=["textbooks"])


def to_textbook_public(textbook: Textbook) -> TextbookPublic:
    return TextbookPublic(id=textbook.id, name=textbook.name)


def to_article_public(article: Article) -> ArticlePublic:
    return ArticlePublic(
        id=article.id,
        textbook_id=article.textbook_id,
        title=article.title,
        content=article.content,
        keywords=article.keywords or [],
        audio_url=article.audio_url,
        sentences=article.sentences or [],
    )


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
    _manager: User = Depends(require_teacher_or_admin),
) -> list[TextbookPublic]:
    textbooks = db.query(Textbook).order_by(Textbook.name.asc()).all()
    return [to_textbook_public(textbook) for textbook in textbooks]


@router.post("", response_model=TextbookPublic, status_code=status.HTTP_201_CREATED)
def create_textbook(
    payload: TextbookCreate,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
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
    _manager: User = Depends(require_teacher_or_admin),
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
    _manager: User = Depends(require_teacher_or_admin),
) -> Response:
    textbook = get_textbook_or_404(textbook_id, db)
    db.delete(textbook)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{textbook_id}/articles", response_model=list[ArticlePublic], status_code=status.HTTP_200_OK)
def list_textbook_articles(
    textbook_id: str,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> list[ArticlePublic]:
    get_textbook_or_404(textbook_id, db)
    articles = db.query(Article).filter(Article.textbook_id == textbook_id).order_by(Article.title.asc()).all()
    return [to_article_public(article) for article in articles]


@router.post("/{textbook_id}/articles", response_model=ArticlePublic, status_code=status.HTTP_201_CREATED)
def create_textbook_article(
    textbook_id: str,
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> ArticlePublic:
    get_textbook_or_404(textbook_id, db)

    article = Article(
        textbook_id=textbook_id,
        title=payload.title,
        content=payload.content,
        keywords=payload.keywords,
        audio_url=payload.audio_url,
        sentences=[sentence.model_dump() for sentence in payload.sentences],
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return to_article_public(article)
