from sqlalchemy import text

from auth import get_password_hash
from database import DATA_DIR, SessionLocal, engine
from models import Base, User, UserType


def drop_article_keywords_column() -> None:
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(articles)")).mappings().all()
        if not any(column["name"] == "keywords" for column in columns):
            return

        connection.execute(text("ALTER TABLE articles DROP COLUMN keywords"))


def init_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    drop_article_keywords_column()

    with SessionLocal() as db:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is not None:
            return

        db.add(
            User(
                username="admin",
                password_hash=get_password_hash("123qwe"),
                user_type=UserType.ADMIN,
            )
        )
        db.commit()
