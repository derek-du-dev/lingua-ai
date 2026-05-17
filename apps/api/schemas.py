from datetime import datetime

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
    keywords: list[str] = Field(default_factory=list)
    audio_url: str = Field(default="", max_length=512)
    sentences: list[ArticleSentence] = Field(default_factory=list)

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

    @field_validator("keywords")
    @classmethod
    def normalize_keywords(cls, value: list[str]) -> list[str]:
        return [keyword.strip() for keyword in value if keyword.strip()]

    @field_validator("audio_url")
    @classmethod
    def normalize_audio_url(cls, value: str) -> str:
        return value.strip()


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    pass


class ArticlePublic(ArticleBase):
    id: str
    textbook_id: str
