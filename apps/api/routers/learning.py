from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Article, ArticleQuestion, Textbook, User
from schemas import (
    LearningAnswerResultItem,
    LearningAnswerSubmission,
    LearningAnswerSubmissionResult,
    LearningArticleDetailPublic,
    LearningArticleQuestionPublic,
    LearningArticleSummaryPublic,
    LearningTextbookPublic,
)

router = APIRouter(prefix="/learning", tags=["learning"])


def to_learning_textbook_public(textbook: Textbook) -> LearningTextbookPublic:
    return LearningTextbookPublic(id=textbook.id, name=textbook.name, article_count=len(textbook.articles))


def to_learning_article_summary_public(article: Article) -> LearningArticleSummaryPublic:
    return LearningArticleSummaryPublic(
        id=article.id,
        textbook_id=article.textbook_id,
        title=article.title,
        question_count=len(article.questions),
    )


def to_learning_article_question_public(question: ArticleQuestion) -> LearningArticleQuestionPublic:
    return LearningArticleQuestionPublic(
        id=question.id,
        article_id=question.article_id,
        question=question.question,
        options=question.options or {},
        difficulty=question.difficulty,
        question_type=question.question_type,
        order_index=question.order_index,
    )


def to_learning_article_detail_public(article: Article) -> LearningArticleDetailPublic:
    questions = sorted(article.questions, key=lambda question: question.order_index)
    return LearningArticleDetailPublic(
        id=article.id,
        textbook_id=article.textbook_id,
        title=article.title,
        content=article.content,
        audio_url=article.audio_url,
        sentences=article.sentences or [],
        key_points=article.key_points or [],
        questions=[to_learning_article_question_public(question) for question in questions],
    )


def get_textbook_or_404(textbook_id: str, db: Session) -> Textbook:
    textbook = db.get(Textbook, textbook_id)
    if textbook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教材不存在")
    return textbook


def get_article_or_404(article_id: str, db: Session) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return article


@router.get("/textbooks", response_model=list[LearningTextbookPublic])
def list_learning_textbooks(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LearningTextbookPublic]:
    textbooks = db.query(Textbook).order_by(Textbook.name.asc()).all()
    return [to_learning_textbook_public(textbook) for textbook in textbooks]


@router.get("/textbooks/{textbook_id}/articles", response_model=list[LearningArticleSummaryPublic])
def list_learning_textbook_articles(
    textbook_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LearningArticleSummaryPublic]:
    get_textbook_or_404(textbook_id, db)
    articles = db.query(Article).filter(Article.textbook_id == textbook_id).order_by(Article.title.asc()).all()
    return [to_learning_article_summary_public(article) for article in articles]


@router.get("/articles/{article_id}", response_model=LearningArticleDetailPublic)
def read_learning_article(
    article_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LearningArticleDetailPublic:
    article = get_article_or_404(article_id, db)
    return to_learning_article_detail_public(article)


@router.post("/articles/{article_id}/answers", response_model=LearningAnswerSubmissionResult)
def submit_learning_article_answers(
    article_id: str,
    payload: LearningAnswerSubmission,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LearningAnswerSubmissionResult:
    get_article_or_404(article_id, db)
    questions = (
        db.query(ArticleQuestion)
        .filter(ArticleQuestion.article_id == article_id)
        .order_by(ArticleQuestion.order_index.asc())
        .all()
    )
    questions_by_id = {question.id: question for question in questions}
    submitted_question_ids = set(payload.answers)
    expected_question_ids = set(questions_by_id)

    if submitted_question_ids - expected_question_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="题目不存在")

    if submitted_question_ids != expected_question_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请完成所有题目后提交")

    items = []
    correct_count = 0
    for question in questions:
        submitted_answer = payload.answers[question.id]
        is_correct = submitted_answer == question.correct_answer
        if is_correct:
            correct_count += 1
        items.append(
            LearningAnswerResultItem(
                question_id=question.id,
                submitted_answer=submitted_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )

    return LearningAnswerSubmissionResult(article_id=article_id, total=len(questions), correct=correct_count, items=items)
