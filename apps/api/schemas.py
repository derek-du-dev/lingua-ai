from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserPublic(BaseModel):
    id: str
    username: str
    user_type: int
    user_type_description: str
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1)
    user_type: int

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        username = value.strip()
        if not username:
            raise ValueError("用户名不能为空")
        return username


class UserUpdate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    user_type: int

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        username = value.strip()
        if not username:
            raise ValueError("用户名不能为空")
        return username


class ResetPasswordResponse(BaseModel):
    message: str


class SystemSettingsUpdate(BaseModel):
    default_password: str = Field(min_length=1)
    edge_tts_rate: float = Field(ge=0, le=1)

    @field_validator("default_password")
    @classmethod
    def normalize_default_password(cls, value: str) -> str:
        password = value.strip()
        if not password:
            raise ValueError("默认密码不能为空")
        return password


class SystemSettingsPublic(SystemSettingsUpdate):
    pass


class TextbookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("教材名称不能为空")
        return name


class TextbookUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=128)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("教材名称不能为空")
        return name


class TextbookPublic(BaseModel):
    id: str
    name: str


class ArticleKeyPointRange(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @field_validator("end")
    @classmethod
    def validate_end(cls, value: int, info) -> int:
        start = info.data.get("start")
        if isinstance(start, int) and value <= start:
            raise ValueError("结束位置必须大于开始位置")
        return value


class ArticleKeyPoint(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    type: Literal["phrase", "selection"]
    text: str = Field(min_length=1, max_length=255)
    abbreviation: str = Field(default="", max_length=64)
    ranges: list[ArticleKeyPointRange] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("重点词不能为空")
        return text

    @field_validator("abbreviation")
    @classmethod
    def normalize_abbreviation(cls, value: str) -> str:
        return value.strip()


class ArticleKeyPointsUpdate(BaseModel):
    key_points: list[ArticleKeyPoint] = Field(default_factory=list)


class ArticleSentence(BaseModel):
    content: str = Field(min_length=1)
    audio_url: str = ""

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("句子内容不能为空")
        return content

    @field_validator("audio_url")
    @classmethod
    def normalize_audio_url(cls, value: str) -> str:
        return value.strip()


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("文章标题不能为空")
        return title

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return value.strip()


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    pass


class ArticleQuestionPublic(BaseModel):
    id: str
    article_id: str
    question: str = Field(min_length=1)
    options: dict[Literal["A", "B", "C", "D"], str]
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    question_type: str = "multiple_choice"
    order_index: int

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: dict[str, str]) -> dict[str, str]:
        expected_keys = {"A", "B", "C", "D"}
        if set(value) != expected_keys:
            raise ValueError("选项必须包含 A、B、C、D")
        normalized = {key: option.strip() for key, option in value.items()}
        if any(not option for option in normalized.values()):
            raise ValueError("选项不能为空")
        return normalized


class ArticlePublic(ArticleBase):
    id: str
    textbook_id: str
    audio_url: str = Field(default="", max_length=512)
    sentences: list[ArticleSentence] = Field(default_factory=list)
    key_points: list[ArticleKeyPoint] = Field(default_factory=list)
    questions: list[ArticleQuestionPublic] = Field(default_factory=list)


class LearningTextbookPublic(BaseModel):
    id: str
    name: str
    article_count: int = 0


class LearningArticleSummaryPublic(BaseModel):
    id: str
    textbook_id: str
    title: str
    question_count: int = 0


class LearningArticleQuestionPublic(BaseModel):
    id: str
    article_id: str
    question: str = Field(min_length=1)
    options: dict[Literal["A", "B", "C", "D"], str]
    difficulty: Optional[str] = None
    question_type: str = "multiple_choice"
    order_index: int

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: dict[str, str]) -> dict[str, str]:
        expected_keys = {"A", "B", "C", "D"}
        if set(value) != expected_keys:
            raise ValueError("选项必须包含 A、B、C、D")
        normalized = {key: option.strip() for key, option in value.items()}
        if any(not option for option in normalized.values()):
            raise ValueError("选项不能为空")
        return normalized


class LearningArticleDetailPublic(ArticleBase):
    id: str
    textbook_id: str
    audio_url: str = Field(default="", max_length=512)
    sentences: list[ArticleSentence] = Field(default_factory=list)
    key_points: list[ArticleKeyPoint] = Field(default_factory=list)
    questions: list[LearningArticleQuestionPublic] = Field(default_factory=list)


class LearningAnswerSubmission(BaseModel):
    answers: dict[str, Literal["A", "B", "C", "D"]]


class LearningAnswerResultItem(BaseModel):
    question_id: str
    submitted_answer: Literal["A", "B", "C", "D"]
    correct_answer: Literal["A", "B", "C", "D"]
    is_correct: bool
    explanation: Optional[str] = None


class LearningAnswerSubmissionResult(BaseModel):
    article_id: str
    total: int
    correct: int
    items: list[LearningAnswerResultItem]
