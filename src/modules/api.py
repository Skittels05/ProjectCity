import json
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache, coder
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
from pydantic import EmailStr
from pydantic.types import UUID
from sqlalchemy.orm import Session
from typing_extensions import Optional
from pathlib import Path

from . import models, schemas, crud, utils
from .config import config_values
from .email import reset_password_message, smtp_check
from .database import SessionLocal


class CacheCoder(coder.Coder):
    @classmethod
    def encode(cls, value: Any) -> bytes:
        return json.dumps(value).encode('utf-8')
    @classmethod
    def decode(cls, value: bytes) -> Any:
        if isinstance(value, bytes):
            return json.loads(value.decode('utf-8'))
        return json.loads(value)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_check(db: Session, token: UUID):
    """Проверка является ли пользователь администратором"""
    db_user = crud.get_user_by_token(db=db, token=token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.role != "admin":
        raise HTTPException(status_code=403, detail="Пользователь не является администратором")


# Цикл работы
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Проверка работы SMTP сервера...")
    config_values.correct_email = smtp_check(
        host=config_values.EMAIL_DOMAIN,
        port=config_values.EMAIL_PORT,
        email=config_values.EMAIL,
        use_tls=config_values.USE_TLS,
        auth=True
    )
    redis = aioredis.from_url(config_values.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="project-city", coder=CacheCoder)
    yield


app = FastAPI(
    title="ProjectCity API",
    description=utils.get_api_doc("api_docs/app.md"),
    version="1.0.0",
    contact={
        "name": "Asriel_Story",
        "url": "https://t.me/Asriel_Story",
        "email": "asriel.story.com@gmail.com"
    },
    lifespan=lifespan
)

static_path = Path(__file__).parent.parent / "uploads"
app.mount(path="/static", app=StaticFiles(directory=str(static_path)), name="static")


# Работа с пользователями
@app.post(
    "/api/v1/user/login",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Авторизация",
    responses={
        200: {"description": "Успешная авторизация"},
        400: {"description": "Некорректные данные (например, логин или пароль не верный)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
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

@app.post(
    "/api/v1/user/register",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Некорректные данные (например, email уже занят)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя в системе"""
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже занят")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    return await crud.create_user(db=db, user=user)

@app.get(
    "/api/v1/user",
    response_model=list[schemas.UserPublic],
    status_code=status.HTTP_200_OK,
    summary="Список пользователей",
    responses={
        200: {"description": "Список пользователей успешно получен"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
@cache(expire=20)
async def users_list(
        page: Optional[int] = None,
        amount: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Получение списка пользователей"""
    if page is None:
        page = 0
    if amount is None or amount > 20:
        amount = 20
    users_data = []
    for user in crud.get_all_users(db=db).limit(amount).offset(page * amount).all():
        users_data.append(
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "rating": user.rating,
                "created_at": str(user.created_at),
                "email_verify": user.email_verify
            }
        )
    return users_data

@app.delete(
    "/api/v1/user",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Удаление пользователя",
    responses={
        200: {"description": "Пользователь успешно удалён"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, токен администратора)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь", "Ограниченный доступ"]
)
async def delete_user(request: schemas.UserDelete, db: Session = Depends(get_db)):
    """Удаление пользователя по его ID через токен администратора"""
    admin_check(db=db, token=request.token)
    db_user = crud.get_user_by_id(db=db, user_id=request.id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Удаляемого пользователя не существует")
    return crud.delete_user(db=db, user_id=request.id)

@app.post(
    "/api/v1/user/verify-email",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Подтверждение почты",
    responses={
        200: {"description": "Почта пользователя успешно подтверждена"},
        400: {"description": "Некорректные данные (например, секретный токен)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def verify_email(request: schemas.VerifyEmail, db: Session = Depends(get_db)):
    """Подтверждение email по токену подтверждения пользователя"""
    db_user = crud.get_user_by_verify_token(db=db, verify_token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Токен не найден")
    return crud.update_user_email_verify(db=db, verify_token=request.token)

@app.post(
    "/api/v1/user/change-password",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Изменение пароля по токену",
    responses={
        200: {"description": "Пароль успешно изменён"},
        400: {"description": "Некорректные данные (например, токен пользователя или пароль)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def change_user_password(request: schemas.ChangePassword, db: Session = Depends(get_db)):
    """Смена пользователем пароля на его аккаунте по токену"""
    db_user = crud.get_user_by_token(db=db, token=request.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not(utils.verify_password(request.old_password, db_user.password)):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    return crud.user_change_password(db=db, token=request.token, new_password=request.new_password)

@app.post(
    "/api/v1/user/forgot-password",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Отправка письма для восcтановления пароля",
    responses={
        200: {"description": "Письмо успешно отправлено"},
        400: {"description": "Некорректные данные или профиль пользователя не активирован (например, свободный email)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    """Отправка письма для восстановления пароля"""
    if email is None:
        raise HTTPException(status_code=400, detail="В запросе отсутствует email")
    db_user = crud.get_user_by_email(db=db, email=email)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Email не занят")
    if not(db_user.email_verify):
        raise HTTPException(status_code=400, detail="Аккаунт не активирован")
    if config_values.correct_email:
        result = await reset_password_message(email=email, verify_token=db_user.verify_token)
    else:
        raise HTTPException(status_code=400, detail="SMTP сервер не работает")
    return  result

@app.post(
    "/api/v1/user/reset-password",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Смена пароля по секретному токену",
    responses={
        200: {"description": "Пароль успешно изменён"},
        400: {"description": "Некорректные данные (например, секретный токен)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
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
@app.post(
    "/api/v1/user/change-role",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Изменение роли пользователя",
    responses={
        200: {"description": "Роль успешно установлена"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, роли не существует в БД)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь", "Ограниченный доступ"]
)
async def change_role(request: schemas.ChangeRole, db: Session = Depends(get_db)):
    """Смена роли пользователя по его ID"""
    admin_check(db=db, token=request.token)
    db_user = crud.get_user_by_id(db=db, user_id=request.user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Изменяемый пользователь не найден")
    db_roles = crud.get_all_roles(db=db).filter(models.Roles.role == request.role).first()
    if db_roles is None:
        raise HTTPException(status_code=400, detail="Роли не существует")
    return crud.change_role(db=db, user_id=request.user_id, role=request.role)

@app.post(
    "/api/v1/user/create-role",
    response_model=schemas.Role,
    status_code=status.HTTP_200_OK,
    summary="Создание роли",
    responses={
        200: {"description": "Роль успешно создана"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, роль уже существует)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь", "Ограниченный доступ"]
)
async def role_create(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Создание новой роли"""
    admin_check(db=db, token=role.token)
    db_roles = crud.get_all_roles(db=db).filter(models.Roles.role == role.role).first()
    if not(db_roles is None):
        raise HTTPException(status_code=400, detail="Роль уже существует")
    return crud.create_role(db=db, role=role)

@app.get(
    "/api/v1/user/issues-count",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Количество проблем пользователя",
    responses={
        200: {"description": "Количество успешно получено"},
        400: {"description": "Некорректные данные (например ID пользователя)"},
        422: {"description": "Ошибка валидации"}
    },
    tags=["Проблемы"]
)
@cache(expire=20)
async def get_user_issues_count(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    """Получение общего числа проблем, созданных пользователем (хранящиеся в БД)"""
    return crud.user_issues_count(db=db, user_id=user_id)


# Работа с проблемами
@app.post(
    "/api/v1/issue/create",
    response_model=schemas.Issue,
    status_code=status.HTTP_200_OK,
    summary="Создание проблемы",
    responses={
        200: {"description": "Проблема успешно создана"},
        400: {"description": "Некорректные данные (например, пользователь не активирован)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы"]
)
async def issue_create(issue: schemas.IssueCreate = Depends(), files: list[UploadFile] = File(None), db: Session = Depends(get_db)):
    """Создание проблемы по токену автора, типу заявки, краткому описанию, подробному описанию и адресу"""
    db_user = crud.get_user_by_token(db=db, token=issue.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not(db_user.email_verify):
        raise HTTPException(status_code=400, detail="Аккаунт не активирован")
    db_issues_fields = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issue.type).first()
    if db_issues_fields is None:
        raise HTTPException(status_code=400, detail="Такого типа проблемы не существует")
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Слишком много файлов")
    for file in files:
        if file.size > 1024 * 1024:
            raise HTTPException(status_code=400, detail="Файл слишком большой")
    return await crud.create_issue(db=db, issue=issue, files=files)

@app.post(
    "/api/v1/issue/status",
    response_model=schemas.Issue,
    status_code=status.HTTP_200_OK,
    summary="Обновление статуса проблемы",
    responses={
        200: {"description": "Статус проблемы успешно обновлён"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, статуса не существует)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы", "Ограниченный доступ"]
)
async def issue_status(issue: schemas.IssueUpdate, db: Session = Depends(get_db)):
    """Обновление статуса проблемы по её ID и ID пользователя (есть проблема, в обработке, выполнено)"""
    db_user = crud.get_user_by_token(db=db, token=issue.token)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    db_issue = crud.get_issue_by_id(db=db, issue_id=issue.id)
    if db_issue is None:
        raise HTTPException(status_code=400, detail="Проблема не найдена")
    if db_user.role != "admin":
        raise HTTPException(status_code=403, detail="Пользователь не является администратором")
    if not(issue.status in crud.STATUSES):
        raise HTTPException(status_code=400, detail="Статуса не существует")
    return await crud.update_issue(db=db, issue=issue)

@app.delete(
    "/api/v1/issue/delete",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Удаление проблемы",
    responses={
        200: {"description": "Проблема успешно удалена"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, проблемы не существует)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы", "Ограниченный доступ"]
)
async  def issue_delete(issue: schemas.IssueDelete, db: Session = Depends(get_db)):
    """Удаление проблемы"""
    admin_check(db=db, token=issue.token)
    db_issue = crud.get_issue_by_id(db=db, issue_id=issue.id)
    if db_issue is None:
        raise HTTPException(status_code=400, detail="Проблема не найдена")
    return crud.delete_issue(db=db, issue=issue)

@app.get(
    "/api/v1/issue/find",
    response_model=list[schemas.Issue],
    status_code=status.HTTP_200_OK,
    summary="Поиск проблемы по параметрам",
    responses={
        200: {"description": "Результат поисков проблем получен"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы"]
)
@cache(expire=20)
async def issue_find(
        issue_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        issue_type: Optional[str] = None,
        short_desc: Optional[str] = None,
        full_desc: Optional[str] = None,
        status: Optional[str] = None,
        address: Optional[str] = None,
        page: Optional[int] = None,
        amount: Optional[int] = None,
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
    if page is None:
        page = 0
    if amount is None or amount > 50:
        amount = 50
    issues_list = []
    for issue in query.limit(amount).offset(page * amount).all():
        issues_list.append({
            "id": str(issue.id),
            "user_id": str(issue.user_id),
            "status": issue.status,
            "type": issue.type,
            "short_desc": issue.short_desc,
            "full_desc": issue.full_desc,
            "address": issue.address,
            "latitude": issue.latitude,
            "longitude": issue.longitude,
            "created_at": str(issue.created_at),
            "updated_at": str(issue.updated_at)
        })
    return issues_list

@app.get(
    "/api/v1/issue/amount",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Количество проблем",
    responses={
        200: {"description": "Количество получено"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы"]
)
@cache(expire=20)
async def issues_amount(db: Session = Depends(get_db)):
    """Получение общего количества проблем"""
    return len(crud.get_all_issues(db=db).all())

@app.get(
    "/api/v1/issue/types",
    response_model=list[schemas.IssuesField],
    status_code=status.HTTP_200_OK,
    summary="Все типы проблем",
    responses={
        200: {"description": "Типы получены"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы"]
)
@cache(expire=20)
async def all_issues_types(db: Session = Depends(get_db)):
    """Получение списка всех типов проблем"""
    issues_type_list = []
    for issues_type in crud.get_all_issues_types(db=db).all():
        issues_type_list.append({
            "type": issues_type.type
        })
    return issues_type_list

@app.post(
    "/api/v1/issue/types",
    response_model=schemas.IssuesField,
    status_code=status.HTTP_200_OK,
    summary="Создание типа проблемы",
    responses={
        200: {"description": "Тип проблемы успешно создан"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, тип уже существует)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы", "Ограниченный доступ"]
)
async def issues_types_create(issues_field: schemas.IssuesFieldCreate, db: Session = Depends(get_db)):
    """Создание нового типа проблем"""
    admin_check(db=db, token=issues_field.token)
    db_issues_types = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issues_field.type).first()
    if db_issues_types:
        raise HTTPException(status_code=400, detail="Тип проблемы уже существует")
    return crud.create_issues_field(db=db, issues_field=issues_field)

@app.delete(
    "/api/v1/issue/types",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="Удаление типа проблемы",
    responses={
        200: {"description": "Тип проблемы успешно удалён"},
        403: {"description": "У пользователя недостаточно прав"},
        400: {"description": "Некорректные данные (например, типа проблемы не существует)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы", "Ограниченный доступ"]
)
async def issues_type_delete(issues_field: schemas.IssuesFieldCreate, db: Session = Depends(get_db)):
    """Удаление типа проблем"""
    admin_check(db=db, token=issues_field.token)
    db_issues_types = crud.get_all_issues_types(db=db).filter(models.IssuesField.type == issues_field.type).first()
    if db_issues_types is None:
        raise HTTPException(status_code=400, detail="Типа проблемы не существует")
    return crud.delete_issues_type(db=db, issues_field=db_issues_types)


# Работа с изображениями
@app.get(
    "/api/v1/photos",
    response_model=list[schemas.Photos],
    summary="Получение ссылок на изображения",
    responses={
        200: {"description": "Ссылки успешно получены"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Проблемы"]
)
@cache(expire=20)
async def get_path_photos(
        photo_id: Optional[UUID] = None,
        issue_id: Optional[UUID] = None,
        page: Optional[int] = None,
        amount: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Получение ссылок на изображения"""
    query = crud.get_all_photos(db=db)
    if photo_id:
        query = query.filter(models.Photos.id == photo_id)
    if issue_id:
        query = query.filter(models.Photos.issue_id == issue_id)
    if page is None:
        page = 0
    if amount is None or amount > 50:
        amount = 50
    photos_list = []
    for photo in query.limit(amount).offset(page * amount).all():
        photos_list.append({
            "id": str(photo.id),
            "issue_id": str(photo.issue_id),
            "file_path": str(photo.file_path)
        })
    return photos_list


# Работа со статистикой
@app.get(
    "/api/v1/statistics/types",
    response_model=list[schemas.StatisticTypes],
    status_code=status.HTTP_200_OK,
    summary="Статистика по типам проблем",
    responses={
        200: {"description": "Статистика получена"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Статистика"]
)
@cache(expire=20)
async def get_statistics_types(db: Session = Depends(get_db)):
    """Получение статистики о проблемах по его типу"""
    return crud.get_statistics_issue_type(db=db)

@app.get(
    "/api/v1/statistics/status",
    response_model=list[schemas.StatisticStatus],
    status_code=status.HTTP_200_OK,
    summary="Статистика по статусам проблем",
    responses={
        200: {"description": "Статистика получена"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Статистика"]
)
@cache(expire=20)
async def get_statistics_status(db: Session = Depends(get_db)):
    """Получение статистики о проблемах по его статусу"""
    return crud.get_statistics_issue_status(db=db)

@app.get(
    "/api/v1/statistics/time",
    response_model=list[schemas.StatisticTime],
    status_code=status.HTTP_200_OK,
    summary="Статистика по времени",
    responses={
        200: {"description": "Статистика получена"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Статистика"]
)
@cache(expire=300)
async def get_statistics_time(db: Session = Depends(get_db)):
    """Получение статистики о проблемах с сортировкой по времени"""
    return crud.get_statistics_time(db=db)

@app.get(
    "/api/v1/statistics/area",
    response_model=list[schemas.StatisticArea],
    status_code=status.HTTP_200_OK,
    summary="Статистика по местности",
    responses={
        200: {"description": "Статистика получена"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Статистика"]
)
@cache(expire=300)
async def get_statistics_area(db: Session = Depends(get_db)):
    """Получение статистики о проблемах с сортировкой по местности"""
    return crud.get_statistics_area(db=db)

@app.get(
    "/api/v1/statistics/average-time",
    response_model=schemas.StatisticAverage,
    status_code=status.HTTP_200_OK,
    summary="Среднее время выполнения",
    responses={
        200: {"description": "Статистика успешно получена"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Статистика"]
)
@cache(expire=300)
async def get_statistics_average(db: Session = Depends(get_db)):
    """Получение статистики о среднем времени по выполнению проблем"""
    return crud.get_statistics_average(db=db)


# Технические запросы
@app.get(
    "/api/health",
    status_code=status.HTTP_200_OK,
    summary="Проверка здоровья",
    responses={
        200: {"description": "Сервер здоров"}
    },
    tags=["Технические запросы"]
)
def health_check():
    """Проверка здоровья сервера"""
    return {"status": "healthy"}
