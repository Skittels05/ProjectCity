from fastapi import FastAPI, HTTPException, status
from . import schemas

app = FastAPI()

@app.post("api/v1/token")
async def login_for_token():
    """Получение токена пользователя, для совершения действий с API"""
    return {"token": "1213131211312"}

@app.post("api/v1/register", response_model=schemas.UserCreate)
async def register(user: schemas.UserCreate):
    """Регистрация пользователя в системе"""
    return ...

