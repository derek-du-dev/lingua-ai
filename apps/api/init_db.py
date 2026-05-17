from sqlalchemy import text

from auth import get_password_hash
from database import DATA_DIR, SessionLocal, engine
from models import Base, User, UserType
from system_settings import get_system_settings


def migrate_articles_table() -> None:
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(articles)")).mappings().all()
        column_names = {column["name"] for column in columns}
        if "keywords" in column_names:
            connection.execute(text("ALTER TABLE articles DROP COLUMN keywords"))
        if "key_points" not in column_names:
            connection.execute(text("ALTER TABLE articles ADD COLUMN key_points JSON NOT NULL DEFAULT '[]'"))


def init_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    migrate_articles_table()

    with SessionLocal() as db:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is not None:
            return

        db.add(
            User(
                username="admin",
                password_hash=get_password_hash(get_system_settings().default_password),
                user_type=UserType.ADMIN,
            )
        )
        db.commit()
