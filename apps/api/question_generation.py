import json
import logging
from typing import Literal, Optional

import httpx
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy.orm import Session

from app_config import get_app_settings
from models import ArticleQuestion

logger = logging.getLogger(__name__)

OPTION_KEYS = {"A", "B", "C", "D"}


class GeneratedArticleQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    options: dict[Literal["A", "B", "C", "D"], str]
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: Optional[str] = Field(default=None, max_length=1000)
    difficulty: Optional[str] = Field(default=None, max_length=32)

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("题目不能为空")
        return question

    @field_validator("options")
    @classmethod
    def normalize_options(cls, value: dict[str, str]) -> dict[str, str]:
        if set(value) != OPTION_KEYS:
            raise ValueError("选项必须包含 A、B、C、D")
        normalized = {key: option.strip() for key, option in value.items()}
        if any(not option for option in normalized.values()):
            raise ValueError("选项不能为空")
        return normalized

    @field_validator("explanation", "difficulty")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = value.strip()
        return text or None


class GeneratedQuestionsResponse(BaseModel):
    difficulty: Optional[str] = Field(default=None, max_length=32)
    questions: list[GeneratedArticleQuestion] = Field(min_length=1)

    @field_validator("difficulty")
    @classmethod
    def normalize_difficulty(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        difficulty = value.strip()
        return difficulty or None


def strip_json_fence(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
    return text


def parse_generated_questions(content: str) -> list[GeneratedArticleQuestion]:
    payload = json.loads(strip_json_fence(content))
    result = GeneratedQuestionsResponse.model_validate(payload)
    difficulty = result.difficulty
    questions: list[GeneratedArticleQuestion] = []
    for question in result.questions:
        if question.difficulty is None:
            question.difficulty = difficulty
        questions.append(question)
    return questions


def build_prompt(title: str, content: str, count: int) -> str:
    return f"""
请基于下面这篇文章，为学生生成 {count} 道匹配文章难度的阅读理解选择题。

要求：
- 先根据文章内容自动判断难度，difficulty 使用 beginner、intermediate 或 advanced。
- 题目必须只考查文章中能得到支持的信息，不要编造背景知识。
- 每题必须有 A、B、C、D 四个选项，且只有一个正确答案。
- 题目和选项优先使用文章语言；解析使用中文。
- 只返回严格 JSON，不要 Markdown，不要代码块，不要额外说明。

返回格式：
{{
  "difficulty": "intermediate",
  "questions": [
    {{
      "question": "...",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "A",
      "explanation": "..."
    }}
  ]
}}

标题：{title}

文章：
{content}
""".strip()


def request_generated_questions(title: str, content: str, count: int) -> list[GeneratedArticleQuestion]:
    settings = get_app_settings()
    if not settings.newapi_api_key:
        logger.warning("LINGUA_NEWAPI_API_KEY is not set; skipping article question generation")
        return []

    request_body = {
        "model": settings.newapi_model,
        "messages": [
            {
                "role": "system",
                "content": "You generate reading-comprehension multiple-choice questions and return valid JSON only.",
            },
            {"role": "user", "content": build_prompt(title, content, count)},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{settings.newapi_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.newapi_api_key}", "Content-Type": "application/json"},
            json=request_body,
        )
        response.raise_for_status()

    response_data = response.json()
    message = response_data["choices"][0]["message"]
    generated_content = message.get("content") or ""
    return parse_generated_questions(generated_content)


def generate_article_questions(title: str, content: str) -> list[GeneratedArticleQuestion]:
    normalized_content = content.strip()
    if not normalized_content:
        return []

    count = get_app_settings().article_question_count
    for attempt in range(2):
        try:
            return request_generated_questions(title, normalized_content, count)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            if attempt == 1:
                logger.exception("Failed to generate article questions")
                return []
            logger.warning("Invalid article question generation response; retrying: %s", exc)
    return []


def replace_article_questions(
    db: Session,
    *,
    article_id: str,
    questions: list[GeneratedArticleQuestion],
) -> list[ArticleQuestion]:
    if not questions:
        return []

    db.query(ArticleQuestion).filter(ArticleQuestion.article_id == article_id).delete()
    question_models = [
        ArticleQuestion(
            article_id=article_id,
            question=question.question,
            options=question.options,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            difficulty=question.difficulty,
            order_index=index,
        )
        for index, question in enumerate(questions)
    ]
    db.add_all(question_models)
    db.flush()
    return question_models
