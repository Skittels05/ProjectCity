from fastapi import FastAPI, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
# from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware
from pydantic.types import UUID
from sqlalchemy import Boolean
from sqlalchemy.orm import Session
from typing_extensions import Optional

from . import models, schemas, crud, utils
from .database import SessionLocal


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/v1/login", response_model=schemas.User)
async def login_for_token(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Получение токена пользователя, для совершения действий с API"""
    if not(user.email is None):
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            utils.verify_password(user.password, db_user)
        else:
            raise HTTPException(status_code=400, detail="Email свободен")
    elif not(user.username is None):
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user:
            utils.verify_password(user.password, db_user)
        else:
            raise HTTPException(status_code=400, detail="Логин свободен")
    else:
        raise HTTPException(status_code=400, detail="Логин или пароль не верный")
    return db_user

@app.post("/api/v1/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя в системе"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже занят")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    return crud.create_user(db=db, user=user)

@app.post("/api/v1/verify-email", response_model=schemas.User, dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def verify_email(request: schemas.VerifyEmail, db: Session = Depends(get_db)):
    """Подтверждение email по токену пользователя"""
    raise HTTPException(status_code=204, detail="В разработке")

@app.post("/api/v1/issue/create", response_model=schemas.Issue)
async def issue_create(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    """Создание проблемы по UUID автора, типу заявки, краткому описанию, подробному описанию и адресу"""
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
    return crud.update_issue(db=db, issue=issue)

@app.post("/api/v1/issue/delete")
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
