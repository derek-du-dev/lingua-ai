from auth import get_password_hash
from database import DATA_DIR, SessionLocal, engine
from models import Base, User, UserType


def init_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

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
