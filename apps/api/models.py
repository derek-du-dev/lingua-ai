from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship
from uuid6 import uuid7

Base = declarative_base()


class UserType(IntEnum):
    STUDENT = 1
    TEACHER = 2
    ADMIN = 3

    @property
    def description(self) -> str:
        descriptions = {
            UserType.STUDENT: "学生",
            UserType.TEACHER: "老师",
            UserType.ADMIN: "管理员",
        }
        return descriptions[self]


def new_uuid7() -> str:
    return str(uuid7())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=new_uuid7)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_type = Column(Integer, nullable=False)


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(String(36), primary_key=True, default=new_uuid7)
    name = Column(String(128), unique=True, index=True, nullable=False)
    articles = relationship("Article", back_populates="textbook", cascade="all, delete-orphan")


class Article(Base):
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=new_uuid7)
    textbook_id = Column(String(36), ForeignKey("textbooks.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=False, default="")
    audio_url = Column(String(512), nullable=False, default="")
    sentences = Column(JSON, nullable=False, default=list)
    key_points = Column(JSON, nullable=False, default=list)

    textbook = relationship("Textbook", back_populates="articles")
    questions = relationship("ArticleQuestion", back_populates="article", cascade="all, delete-orphan")


class ArticleQuestion(Base):
    __tablename__ = "article_questions"

    id = Column(String(36), primary_key=True, default=new_uuid7)
    article_id = Column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(32), nullable=True)
    question_type = Column(String(32), nullable=False, default="multiple_choice")
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="questions")
