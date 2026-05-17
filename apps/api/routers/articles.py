from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from article_processing import build_article_assets
from auth import require_teacher_or_admin
from database import get_db
from models import Article, User
from schemas import ArticlePublic, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


def to_article_public(article: Article) -> ArticlePublic:
    return ArticlePublic(
        id=article.id,
        textbook_id=article.textbook_id,
        title=article.title,
        content=article.content,
        audio_url=article.audio_url,
        sentences=article.sentences or [],
    )


def get_article_or_404(article_id: str, db: Session) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return article


@router.put("/{article_id}", response_model=ArticlePublic)
def update_article(
    article_id: str,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> ArticlePublic:
    article = get_article_or_404(article_id, db)
    content, audio_url, sentences = build_article_assets(article.id, payload.content)
    article.title = payload.title
    article.content = content
    article.audio_url = audio_url
    article.sentences = sentences
    db.commit()
    db.refresh(article)
    return to_article_public(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: str,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> Response:
    article = get_article_or_404(article_id, db)
    db.delete(article)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
