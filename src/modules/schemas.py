from pydantic import BaseModel, EmailStr, Field
from pydantic.types import UUID
from typing import Optional
from datetime import datetime, timedelta


# Пользовательские классы
class UserBase(BaseModel):
    username: str = Field(
        default=...,
        max_length=50,
        examples=["John", "Mike", "Asriel"],
        description="Имя пользователя"
    )
    email: EmailStr = Field(
        default=...,
        max_length=100,
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Электронная почта пользователя"
    )

class UserCreate(UserBase):
    password: str = Field(
        default=...,
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Пароль создаваемого пользователя"
    )

class User(UserBase):
    id: UUID = Field(
        default=...,
        examples=["e7c27ed6-a9ae-472c-b8bb-b7e961b07b8d"],
        description="ID пользователя указанный в формате UUID"
    )
    role: str = Field(
        default=...,
        max_length=20,
        examples=["user", "admin"],
        description="Роль пользователя для определения его возможностей"
    )
    rating: int = Field(
        default=...,
        examples=[0, 23, 42],
        description="Рейтинг пользователя"
    )
    created_at: datetime = Field(
        default=...,
        examples=[datetime.now() - timedelta(days=1)],
        description="Дата в которую был создан профиль"
    )
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя для взаимодействия с частями API"
    )
    email_verify: bool = Field(
        default=...,
        examples=[True, False],
        description="Значение, отображающее подтверждена ли почта пользователя"
    )

class UserPublic(UserBase):
    id: UUID = Field(
        default=...,
        examples=["e7c27ed6-a9ae-472c-b8bb-b7e961b07b8d"],
        description="ID пользователя указанный в формате UUID"
    )
    role: str = Field(
        default=...,
        max_length=20,
        examples=["user", "admin"],
        description="Роль пользователя для определения его возможностей"
    )
    rating: int = Field(
        default=...,
        examples=[0, 23, 42],
        description="Рейтинг пользователя"
    )
    email_verify: bool = Field(
        default=...,
        examples=[True, False],
        description="Значение, отображающее подтверждена ли почта пользователя"
    )
    created_at: datetime = Field(
        default=...,
        examples=[datetime.now() - timedelta(days=1)],
        description="Дата в которую был создан профиль"
    )

class UserLogin(BaseModel):
    email: Optional[EmailStr] = Field(
        default=...,
        max_length=100,
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Необязательное поле почты пользователя, предназначенное для поиска пользователя"
    )
    username: Optional[str] = Field(
        default=...,
        max_length=50,
        examples=["John", "Mike", "Asriel"],
        description="Необязательное поле имени профиля пользователя, предназначенное для поиска пользователя"
    )
    password: str = Field(
        default=...,
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Пароль пользователя"
    )

class UserDelete(BaseModel):
    id: UUID = Field(
        default=...,
        examples=["e7c27ed6-a9ae-472c-b8bb-b7e961b07b8d"],
        description="ID удаляемого пользователя, выраженное в виде UUID"
    )
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя имеющего право на удаление"
    )

class VerifyEmail(BaseModel):
    token: UUID = Field(
        default=...,
        examples=["d9e9d8e2-be1e-4697-8ea9-484b7dd67c70"],
        description="Секретный токен пользователя, для подтверждения почты"
    )

class ChangePassword(BaseModel):
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, который хочет поменять пароль"
    )
    old_password: str = Field(
        default=...,
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Старый пароль пользователя, подтверждающий его действие"
    )
    new_password: str = Field(
        default=...,
        min_length=8,
        max_length=32,
        examples=["qwerty", "12345678", "qwerty25"],
        description="Новый пароль пользователя"
    )

class ChangeRole(BaseModel):
    user_id: UUID = Field(
        default=...,
        examples=["e7c27ed6-a9ae-472c-b8bb-b7e961b07b8d"],
        description="ID пользователя, которому будет изменена роль, выраженный в виде UUID"
    )
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, имеющего право на изменение роли"
    )
    role: str = Field(
        default=...,
        max_length=20,
        examples=["user", "admin"],
        description="Название роли на которую меняют нынешнюю роль"
    )

class RoleCreate(BaseModel):
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, имеющего право на создание роли"
    )
    role: str = Field(
        default=...,
        max_length=20,
        examples=["fireman"],
        description="Название создаваемой роли"
    )

class Role(BaseModel):
    role: str = Field(
        default=...,
        max_length=20,
        examples=["user", "admin", "fireman"],
        description="Название роли"
    )


# Классы проблем
class IssueCreate(BaseModel):
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, создающего проблему"
    )
    type: str = Field(
        default=...,
        max_length=50,
        examples=["Дорожная", "Освещение"],
        description="Тип проблемы, который должен храниться в БД"
    )
    short_desc: str = Field(
        default=...,
        max_length=200,
        examples=["Яма на дороге", "Не работает свет в подъезде"],
        description="Краткое описание проблемы"
    )
    full_desc: str = Field(
        default=...,
        max_length=10000,
        examples=["Яма на дороге уже месяц на дороге, почините пожалуйста", "Выходить в ночью просто нереально, ничего не видно"],
        description="Подробное описание проблемы"
    )
    address: str = Field(
        default=...,
        max_length=255,
        examples=["улица Ленина, 13, Смоленск, 214033"],
        description="Адрес по которому произошла проблема"
    )
    latitude: float = Field(
        default=...,
        ge=-90.0,
        le=90.0,
        examples=[54.782801],
        description="Широта точки для нахождения её на карте"
    )
    longitude: float = Field(
        default=...,
        ge=-180.0,
        le=180.0,
        examples=[32.051162],
        description="Долгота точки для нахождения её на карте"
    )

class Issue(BaseModel):
    id: UUID = Field(
        default=...,
        examples=["fd082294-4eba-404b-a40a-802614f0363b"],
        description="ID проблемы, указанный в виде UUID"
    )
    user_id: UUID = Field(
        default=...,
        examples=["e7c27ed6-a9ae-472c-b8bb-b7e961b07b8d"],
        description="ID пользователя, создавшего эту проблему, указан ID в виде UUID"
    )
    status: str = Field(
        default=...,
        max_length=20,
        examples=["есть проблема", "в обработке", "выполнено"],
        description='Статус проблемы (бывают "есть проблема", "в обработке", "выполнено")'
    )
    type: str = Field(
        default=...,
        max_length=50,
        examples=["Дорожная", "Освещение"],
        description="Тип проблемы, который должен храниться в БД"
    )
    short_desc: str = Field(
        default=...,
        max_length=200,
        examples=["Яма на дороге", "Не работает свет в подъезде"],
        description="Краткое описание проблемы"
    )
    full_desc: str = Field(
        default=...,
        max_length=10000,
        examples=["Яма на дороге уже месяц на дороге, почините пожалуйста", "Выходить в ночью просто нереально, ничего не видно"],
        description="Подробное описание проблемы"
    )
    address: str = Field(
        default=...,
        max_length=255,
        examples=["улица Ленина, 13, Смоленск, 214033"],
        description="Адрес по которому произошла проблема"
    )
    latitude: float = Field(
        default=...,
        ge=-90.0,
        le=90.0,
        examples=[54.782801],
        description="Широта точки для нахождения её на карте"
    )
    longitude: float = Field(
        default=...,
        ge=-180.0,
        le=180.0,
        examples=[32.051162],
        description="Долгота точки для нахождения её на карте"
    )
    created_at: datetime = Field(
        default=...,
        examples=[datetime.now() - timedelta(days=1)],
        description="Время в которое была создана проблема, выражено в TIMESTAMP"
    )
    updated_at: datetime = Field(
        default=...,
        examples=[datetime.now()],
        description="Время в которое был последний раз обновлён статус проблемы, выражено в TIMESTAMP"
    )

class IssueUpdate(BaseModel):
    id: UUID = Field(
        default=...,
        examples=["fd082294-4eba-404b-a40a-802614f0363b"],
        description="ID проблемы статус которой будет изменён, указанный в виде UUID"
    )
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, имеющего право на изменение статуса проблемы"
    )
    status: str = Field(
        default=...,
        max_length=20,
        examples=["есть проблема", "в обработке", "выполнено"],
        description="Новый статус проблемы, которым необходимо заменить старый статус"
    )

class IssueDelete(BaseModel):
    id: UUID = Field(
        default=...,
        examples=["fd082294-4eba-404b-a40a-802614f0363b"],
        description="ID удаляемой проблемы, выраженной в UUID"
    )
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, имеющего право на удаление проблемы"
    )

class IssuesField(BaseModel):
    type: str = Field(
        default=...,
        examples=["Яма на дороге", "Не работает свет в подъезде", "Водоснабжение"],
        description="Тип возможной проблемы"
    )

class IssuesFieldCreate(IssuesField):
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен пользователя, имеющего право на добавление новых типов проблем"
    )


class Request(BaseModel):
    token: UUID = Field(
        default=...,
        examples=["e0cc4347-9d2b-4505-ab09-f0ccf46e3695"],
        description="Токен предназначенный для запроса"
    )
