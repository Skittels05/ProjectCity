from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas
from .utils import get_password_hash


def get_user_by_username(db: Session, username: str):
    """Получение класса пользователя по имени пользователя"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Получение класса пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Создание поля нового пользователя по его классу"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        id=uuid4(),
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_admin=False,
        rating=0,
        created_at=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
