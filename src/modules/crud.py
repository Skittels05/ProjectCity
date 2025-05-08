from uuid import uuid4
from pydantic.types import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas, email
from .utils import get_password_hash

STATUSES = ["есть проблема", "в обработке", "выполнено"]

# Работа с пользователями
def get_user_by_id(db: Session, user_id: UUID):
    """Получение класса пользователя по его ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Получение класса пользователя по имени пользователя"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Получение класса пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_token(db: Session, token: UUID):
    """Получение класса пользователя по ID"""
    return db.query(models.User).filter(models.User.token == token).first()

def get_user_by_verify_token(db: Session, verify_token: UUID):
    """Получение класса пользователя по подтверждающему токену"""
    return db.query(models.User).filter(models.User.verify_token == verify_token).first()

def update_user_token(db: Session, user_id: UUID):
    """Обновление токена пользователя по его ID"""
    db_user = get_user_by_id(db=db, user_id=user_id)
    db_user.token = uuid4()
    db.commit()
    db.refresh(db_user)
    return db_user

def is_activated(db: Session, user_id: UUID) -> bool:
    """Получение значения активации профиля"""
    return db.query(models.User).filter(models.User.id == user_id).first().email_verify


# Работа с проблемами
def get_all_issues_types(db: Session):
    return db.query(models.IssuesField)

def get_all_issues(db: Session):
    """Получение всех проблем"""
    return db.query(models.Issue)

def get_issue_by_id(db: Session, issue_id: UUID):
    """Получение проблемы по его ID"""
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()


# Работа со статистикой
def get_statistics_issue_type(db: Session) -> list[dict]:
    """Получение списка статистики по типам проблем"""
    statistics_list = []
    db_issues = db.query(models.Issue)
    db_issues_fields = get_all_issues_types(db=db).all()
    for issue_field in db_issues_fields:
        statistics_list.append(
            {
                "type": issue_field.type,
                "count": len(db_issues.filter(models.Issue.type == issue_field.type).all())
            }
        )
    return statistics_list

def get_statistics_issue_status(db: Session) -> list[dict]:
    """Получение списка статистики по статусу проблемы"""
    statistics_list = []
    db_issues = db.query(models.Issue)
    for status in STATUSES:
        statistics_list.append(
            {
                "status": status,
                "count": len(db_issues.filter(models.Issue.status == status).all())
            }
        )
    return statistics_list


# Работа с ролями
def get_all_roles(db: Session):
    """Функция для получения всех ролей"""
    return db.query(models.Roles)


# Создание полей
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
    email.send_verification_email(db_user.email, db_user.verify_token)
    return db_user

def create_issue(db: Session, issue: schemas.IssueCreate) -> models.Issue:
    """Создание поля новой проблемы по его классу"""
    db_issue = models.Issue(
        id=uuid4(),
        user_id=get_user_by_token(db=db, token=issue.token).id,
        type=issue.type,
        short_desc=issue.short_desc,
        full_desc=issue.full_desc,
        status=STATUSES[0],
        address=issue.address
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def create_issues_field(db: Session, issues_field: schemas.IssuesField):
    """Создание нового типа проблемы"""
    db_issues_field = models.IssuesField(
        type=issues_field.type
    )
    db.add(db_issues_field)
    db.commit()
    db.refresh(db_issues_field)
    return db_issues_field

def create_role(db: Session, role: schemas.RoleCreate):
    """Создание новой роли"""
    db_role = models.Roles(
        role=role.role
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


# Изменение полей
def update_user_verify_token(db: Session, user_id: UUID):
    """Обновление подтверждающего токена"""
    db_user = get_user_by_id(db=db, user_id=user_id)
    db_user.verify_token = uuid4()
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_email_verify(db: Session, verify_token: UUID):
    """Обновление подтверждения почты"""
    db_user = get_user_by_verify_token(db=db, verify_token=verify_token)
    db_user.email_verify = True
    db_user = update_user_verify_token(db=db, user_id=db_user.id)
    db.commit()
    db.refresh(db_user)
    return db_user

def user_change_password(db: Session, new_password: str, token: UUID = None, verify_token: UUID = None):
    """Функция изменения пароля в БД"""
    if not(token is None):
        db_user = get_user_by_token(db=db, token=token)
    elif not(verify_token is None):
        db_user = get_user_by_verify_token(db=db, verify_token=verify_token)
    else:
        raise ValueError("Токен не был введён")
    db_user.password = get_password_hash(new_password)
    db_user.token = uuid4()
    db_user.verify_token = uuid4()
    db.commit()
    db.refresh(db_user)
    return db_user

def change_role(db: Session, user_id: UUID, role: str):
    """Изменение роли у пользователя по его ID"""
    db_user = get_user_by_id(db=db, user_id=user_id)
    db_user.role = role
    db.commit()
    db.refresh(db_user)
    return db_user

def update_issue(db: Session, issue: schemas.IssueUpdate):
    """Обновление поля статуса"""
    db_issue = get_issue_by_id(db=db, issue_id=issue.id)
    db_issue.status = issue.status
    email.send_notification_status(email=get_user_by_id(db=db, user_id=db_issue.user_id).email, issue=db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def delete_user(db: Session, user_id: UUID):
    """Функция удаления пользователя по его ID"""
    db_user = get_user_by_id(db=db, user_id=user_id)
    db.delete(db_user)
    db.commit()
    return 200

def delete_issue(db: Session, issue: schemas.IssueDelete):
    """Удаление проблемы из БД"""
    db_issue = get_issue_by_id(db=db, issue_id=issue.id)
    db.delete(db_issue)
    db.commit()
    return 200

def delete_issues_type(db: Session, issues_field: schemas.IssuesFieldCreate):
    """Удаление типа проблем из БД"""
    db.delete(issues_field)
    db.commit()
    return 200
