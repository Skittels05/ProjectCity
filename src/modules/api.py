from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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
