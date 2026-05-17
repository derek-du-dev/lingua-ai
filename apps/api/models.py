from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
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
