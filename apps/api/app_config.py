from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent / ".env"


class AppSettings(BaseSettings):
    jwt_secret: Optional[str] = None
    tts_voice: str = "en-US-JennyNeural"
    newapi_api_key: Optional[str] = None
    newapi_base_url: str = "https://newapi.aigoconnection.com/v1"
    newapi_model: str = "gemini-2.5-flash"
    article_question_count: int = 5

    model_config = SettingsConfigDict(
        env_prefix="LINGUA_",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret", "newapi_api_key")
    @classmethod
    def normalize_optional_secret(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        secret = value.strip()
        return secret or None

    @field_validator("tts_voice", "newapi_base_url", "newapi_model")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("配置不能为空")
        return text

    @field_validator("newapi_base_url")
    @classmethod
    def normalize_newapi_base_url(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("article_question_count", mode="before")
    @classmethod
    def normalize_article_question_count(cls, value) -> int:
        try:
            count = int(value)
        except (TypeError, ValueError):
            count = 5
        return max(1, min(10, count))


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()
