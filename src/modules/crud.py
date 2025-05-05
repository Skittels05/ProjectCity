from uuid import uuid4
from pydantic.types import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas, email
from .utils import get_password_hash


def get_user_by_username(db: Session, username: str):
    """Получение класса пользователя по имени пользователя"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Получение класса пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_token(db: Session, token: UUID):
    """Получение класса пользователя по ID"""
    return db.query(models.User).filter(models.User.token == token).first()

def get_all_issues(db: Session):
    """Получение всех проблем"""
    return db.query(models.Issue)

def get_issue_by_id(db: Session, issue_id: UUID):
    """Получение проблемы по его ID"""
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Создание поля нового пользователя по его классу"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        id=uuid4(),
        username=user.username,
        email=user.email,
        password=hashed_password,
        role='user',
        rating=0,
        created_at=datetime.now(),
        token=uuid4(),
        email_verify=False,
        verify_token=uuid4()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # email.send_verification_email(db_user.email, db_user.verify_token)
    return db_user

def create_issue(db: Session, issue: schemas.IssueCreate) -> models.Issue:
    """Создание поля новой проблемы по его классу"""
    db_issue = models.Issue(
        id=uuid4(),
        user_id=issue.user_id,
        type=issue.type,
        short_desc=issue.short_desc,
        full_desc=issue.full_desc,
        status='новая',
        address=issue.address
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def update_issue(db: Session, issue: schemas.IssueUpdate):
    """Обновление поля статуса"""
    # TODO Добавить обработку ошибки (в этом случае вернуть БД в прежнее состояние)
    db_issue = get_issue_by_id(db=db, issue_id=issue.id)
    db_issue.status = issue.status
    db.commit()
    db.refresh(db_issue)
    return db_issue

def delete_issue(db: Session, issue: schemas.IssueDelete):
    """Удаление проблемы из БД"""
    db_issue = get_issue_by_id(db=db, issue_id=issue.id)
    db.delete(db_issue)
    db.commit()
    return 200
