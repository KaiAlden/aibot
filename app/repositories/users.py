from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username, User.is_active.is_(True)))


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
