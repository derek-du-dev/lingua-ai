from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from article_processing import build_article_assets
from auth import get_current_user, require_teacher_or_admin
from database import get_db
from models import Article, ArticleQuestion, User
from question_generation import generate_article_questions, replace_article_questions
from schemas import ArticleKeyPointsUpdate, ArticlePublic, ArticleQuestionPublic, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


def to_article_question_public(question: ArticleQuestion) -> ArticleQuestionPublic:
    return ArticleQuestionPublic(
        id=question.id,
        article_id=question.article_id,
        question=question.question,
        options=question.options or {},
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        difficulty=question.difficulty,
        question_type=question.question_type,
        order_index=question.order_index,
    )


def to_article_public(article: Article) -> ArticlePublic:
    questions = sorted(article.questions, key=lambda question: question.order_index)
    return ArticlePublic(
        id=article.id,
        textbook_id=article.textbook_id,
        title=article.title,
        content=article.content,
        audio_url=article.audio_url,
        sentences=article.sentences or [],
        key_points=article.key_points or [],
        questions=[to_article_question_public(question) for question in questions],
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

    generated_questions = generate_article_questions(article.title, article.content)
    if generated_questions:
        replace_article_questions(db, article_id=article.id, questions=generated_questions)
        db.commit()
        db.refresh(article)

    return to_article_public(article)


@router.get("/{article_id}/questions", response_model=list[ArticleQuestionPublic])
def list_article_questions(
    article_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[ArticleQuestionPublic]:
    get_article_or_404(article_id, db)
    questions = (
        db.query(ArticleQuestion)
        .filter(ArticleQuestion.article_id == article_id)
        .order_by(ArticleQuestion.order_index.asc())
        .all()
    )
    return [to_article_question_public(question) for question in questions]


@router.post("/{article_id}/questions/regenerate", response_model=list[ArticleQuestionPublic])
def regenerate_article_questions(
    article_id: str,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> list[ArticleQuestionPublic]:
    article = get_article_or_404(article_id, db)
    generated_questions = generate_article_questions(article.title, article.content)
    if not generated_questions:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="练习题生成失败")

    questions = replace_article_questions(db, article_id=article.id, questions=generated_questions)
    db.commit()
    return [to_article_question_public(question) for question in questions]


@router.put("/{article_id}/key-points", response_model=ArticlePublic)
def update_article_key_points(
    article_id: str,
    payload: ArticleKeyPointsUpdate,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_teacher_or_admin),
) -> ArticlePublic:
    article = get_article_or_404(article_id, db)
    article.key_points = [key_point.model_dump() for key_point in payload.key_points]
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
