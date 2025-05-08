from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
# from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from pydantic.types import UUID
from sqlalchemy.orm import Session
from typing_extensions import Optional

from . import models, schemas, crud, utils
from .email import reset_password_message
from .crud import update_user_email_verify
from .database import SessionLocal


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Работа с пользователями
@app.post("/api/v1/user/login", response_model=schemas.User)
async def login_for_token(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Получение токена пользователя, для совершения действий с API"""
    if not(user.email is None):
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user is None:
            raise HTTPException(status_code=400, detail="Email свободен")
    elif not(user.username is None):
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user is None:
            raise HTTPException(status_code=400, detail="Логин свободен")
    else:
        raise HTTPException(status_code=400, detail="Не были указаны данные")
    if not(utils.verify_password(user.password, db_user.password)):
        raise HTTPException(status_code=400, detail="Логин или пароль не верный")
    return db_user

@app.post("/api/v1/user/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя в системе"""
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже занят")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    return crud.create_user(db=db, user=user)

@app.delete("/api/v1/user")
async def delete_user(request: schemas.UserDelete, db: Session = Depends(get_db)):
    """Удаление пользователя по его ID через токен администратора"""
    db_user = crud.get_user_by_token(db=db, token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    db_user = crud.get_user_by_id(db=db, user_id=request.id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Удаляемого пользователя не существует")
    return crud.delete_user(db=db, user_id=request.id)

@app.post("/api/v1/user/verify-email", response_model=schemas.User)
async def verify_email(request: schemas.VerifyEmail, db: Session = Depends(get_db)):
    """Подтверждение email по токену подтверждения пользователя"""
    db_user = crud.get_user_by_verify_token(db=db, verify_token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Токен не найден")
    return crud.update_user_email_verify(db=db, verify_token=request.token)

@app.post("/api/v1/user/change-password", response_model=schemas.User)
async def change_user_password(request: schemas.ChangePassword, db: Session = Depends(get_db)):
    """Смена пользователем пароля на его аккаунте по токену"""
    db_user = crud.get_user_by_token(db=db, token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not(utils.verify_password(request.old_password, db_user.password)):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    return crud.user_change_password(db=db, token=request.token, new_password=request.new_password)

@app.post("/api/v1/user/forgot-password")
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    """Отправка письма для восстановления пароля"""
    if email is None:
        raise HTTPException(status_code=400, detail="В запросе отсутствует email")
    db_user = crud.get_user_by_email(db=db, email=email)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Email не занят")
    if not(db_user.email_verify):
        raise HTTPException(status_code=400, detail="Аккаунт не активирован")
    return reset_password_message(email=email, verify_token=db_user.verify_token)

@app.post("/api/v1/user/reset-password", response_model=schemas.User)
async def reset_password(verify_token: UUID, new_password: str, db: Session = Depends(get_db)):
    """Сброс пароля пользователя по секретному токену"""
    if verify_token is None:
        raise HTTPException(status_code=400, detail="В запросе отсутствует токен")
    if new_password is None:
        raise HTTPException(status_code=400, detail="В запросе отсутствует пароль")
    db_user = crud.get_user_by_verify_token(db=db, verify_token=verify_token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Неверный токен")
    return crud.user_change_password(db=db, verify_token=verify_token, new_password=new_password)


# Работа с ролями
@app.post("/api/v1/user/change-role", response_model=schemas.User)
async def change_role(request: schemas.ChangeRole, db: Session = Depends(get_db)):
    """Смена роли пользователя по его ID"""
    db_user = crud.get_user_by_token(db=db, token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    db_user = crud.get_user_by_id(db=db, user_id=request.user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Изменяемый пользователь не найден")
    db_roles = crud.get_all_roles(db=db).filter(models.Roles.role == request.role).first()
    if db_roles is None:
        raise HTTPException(status_code=400, detail="Роли не существует")
    return crud.change_role(db=db, user_id=request.user_id, role=request.role)

@app.post("/api/v1/user/create-role", response_model=schemas.Role)
async def role_create(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Создание новой роли"""
    db_user = crud.get_user_by_token(db=db, token=role.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    db_roles = crud.get_all_roles(db=db).filter(models.Roles.role == role.role).first()
    if not(db_roles is None):
        raise HTTPException(status_code=400, detail="Роль уже существует")
    return crud.create_role(db=db, role=role)



# Работа с проблемами
@app.post("/api/v1/issue/create", response_model=schemas.Issue)
async def issue_create(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    """Создание проблемы по токену автора, типу заявки, краткому описанию, подробному описанию и адресу"""
    db_user = crud.get_user_by_token(db=db, token=issue.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not(db_user.email_verify):
        raise HTTPException(status_code=400, detail="Аккаунт не активирован")
    db_issues_fields = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issue.type).first()
    if db_issues_fields is None:
        raise HTTPException(status_code=400, detail="Такого типа проблемы не существует")
    return crud.create_issue(db=db, issue=issue)

@app.post("/api/v1/issue/status", response_model=schemas.Issue)
async def issue_status(issue: schemas.IssueUpdate, db: Session = Depends(get_db)):
    """Обновление статуса проблемы по её ID и ID пользователя"""
    db_user = crud.get_user_by_token(db=db, token=issue.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    db_issue = crud.get_issue_by_id(db=db, issue_id=issue.id)
    if db_issue is None:
        raise HTTPException(status_code=400, detail="Проблема не найдена")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    if not(issue.status in crud.STATUSES):
        raise HTTPException(status_code=400, detail="Статуса не существует")
    return crud.update_issue(db=db, issue=issue)

@app.delete("/api/v1/issue/delete")
async  def issue_delete(issue: schemas.IssueDelete, db: Session = Depends(get_db)):
    """Удаление проблемы"""
    db_user = crud.get_user_by_token(db=db, token=issue.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    db_issue = crud.get_issue_by_id(db=db, issue_id=issue.id)
    if db_issue is None:
        raise HTTPException(status_code=400, detail="Проблема не найдена")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    return crud.delete_issue(db=db, issue=issue)

@app.post("/api/v1/issue/find")
# @cache(expire=60)
async def issue_find(
        issue_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        issue_type: Optional[str] = None,
        short_desc: Optional[str] = None,
        full_desc: Optional[str] = None,
        status: Optional[str] = None,
        address: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Поиск проблемы по её параметрам"""
    query = crud.get_all_issues(db=db)
    if issue_id:
        query = query.filter(models.Issue.id == issue_id)
    if user_id:
        query = query.filter(models.Issue.user_id == user_id)
    if issue_type:
        query = query.filter(models.Issue.type == issue_type)
    if short_desc:
        query = query.filter(models.Issue.short_desc == short_desc)
    if full_desc:
        query = query.filter(models.Issue.full_desc == full_desc)
    if status:
        query = query.filter(models.Issue.status == status)
    if address:
        query = query.filter(models.Issue.address == address)
    return query.all()

@app.get("/api/v1/issue/types")
async def all_issues_types(db: Session = Depends(get_db)):
    """Получение списка всех типов проблем"""
    return crud.get_all_issues_types(db=db).all()

@app.post("/api/v1/issue/types")
async def issues_types_create(issues_field: schemas.IssuesFieldCreate, db: Session = Depends(get_db)):
    """Создание нового типа проблем"""
    db_user = crud.get_user_by_token(db=db, token=issues_field.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    db_issues_types = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issues_field.type).first()
    if db_issues_types:
        raise HTTPException(status_code=400, detail="Тип проблемы уже существует")
    return crud.create_issues_field(db=db, issues_field=issues_field)

@app.delete("/api/v1/issue/types")
async def issues_type_delete(issues_field: schemas.IssuesFieldCreate, db: Session = Depends(get_db)):
    """Удаление типа проблем"""
    db_user = crud.get_user_by_token(db=db, token=issues_field.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="Пользователь не является администратором")
    db_issues_types = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issues_field.type).first()
    return crud.delete_issues_type(db=db, issues_field=db_issues_types)


# Работа со статистикой
@app.get("/api/v1/statistics/types")
async def get_statistics_types(db: Session = Depends(get_db)):
    """Получение статистики о проблемах по его типу"""
    return crud.get_statistics_issue_type(db=db)

@app.get("/api/v1/statistics/status")
async def get_statistics_status(db: Session = Depends(get_db)):
    """Получение статистики о проблемах по его статусу"""
    return crud.get_statistics_issue_status(db=db)
