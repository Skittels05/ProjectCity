from pydantic import BaseModel, EmailStr, Field
from pydantic.types import UUID
import datetime


# Пользовательские классы
class UserBase(BaseModel):
    username: str = Field(default=..., description="Имя пользователя")
    email: EmailStr = Field(default=..., description="Электронная почта пользователя")

class UserCreate(UserBase):
    password: str = Field(default=..., description="Пароль создаваемого пользователя")

class User(UserBase):
    id: UUID = Field(default=..., description="ID пользователя указанный в формате UUID")
    role: str = Field(default=..., description="Роль пользователя для определения его возможностей")
    token: UUID = Field(default=..., description="Токен пользователя для взаимодействия с частями API")
    email_verify: bool = Field(default=..., description="Значение, отображающее подтверждена ли почта пользователя")

class UserLogin(BaseModel):
    email: EmailStr | None = Field(default=..., description="Необязательное поле почты пользователя, предназначенное для поиска пользователя")
    username: str | None = Field(default=..., description="Необязательное поле имени профиля пользователя, предназначенное для поиска пользователя")
    password: str = Field(default=..., description="Пароль пользователя")

class UserDelete(BaseModel):
    id: UUID = Field(default=..., description="ID удаляемого пользователя, выраженное в виде UUID")
    token: UUID = Field(default=..., description="Токен пользователя имеющего право на удаление")

class VerifyEmail(BaseModel):
    token: UUID = Field(default=..., description="Секретный токен пользователя, для подтверждения почты")

class ChangePassword(BaseModel):
    token: UUID = Field(default=..., description="Токен пользователя, который хочет поменять пароль")
    old_password: str = Field(default=..., description="Старый пароль пользователя, подтверждающий его действие")
    new_password: str = Field(default=..., description="Новый пароль пользователя")

class ChangeRole(BaseModel):
    user_id: UUID = Field(default=..., description="ID пользователя, которому будет изменена роль, выраженный в виде UUID")
    token: UUID = Field(default=..., description="Токен пользователя, имеющего право на изменение роли")
    role: str = Field(default=..., description="Название роли на которую меняют нынешнюю роль")

class RoleCreate(BaseModel):
    token: UUID = Field(default=..., description="Токен пользователя, имеющего право на создание роли")
    role: str = Field(default=..., description="Название создаваемой роли")

class Role(BaseModel):
    role: str = Field(default=..., description="Название роли")


# Классы проблем
class IssueCreate(BaseModel):
    token: UUID = Field(default=..., description="Токен пользователя, создающего проблему")
    type: str = Field(default=..., description="Тип проблемы, который должен храниться в БД")
    short_desc: str = Field(default=..., description="Краткое описание проблемы")
    full_desc: str = Field(default=..., description="Подробное описание проблемы")
    address: str = Field(default=..., description="Адрес по которому произошла проблема")

class Issue(BaseModel):
    id: UUID = Field(default=..., description="ID проблемы, указанный в виде UUID")
    user_id: UUID = Field(default=..., description="ID пользователя, создавшего эту проблему, указан ID в виде UUID")
    status: str = Field(default=..., description='Статус проблемы (бывают "есть проблема", "в обработке", "выполнено")')
    type: str = Field(default=..., description="Тип проблемы, который должен храниться в БД")
    short_desc: str = Field(default=..., description="Краткое описание проблемы")
    full_desc: str = Field(default=..., description="Подробное описание проблемы")
    address: str = Field(default=..., description="Адрес по которому произошла проблема")

class IssueUpdate(BaseModel):
    id: UUID = Field(default=..., description="ID проблемы статус которой будет изменён, указанный в виде UUID")
    token: UUID = Field(default=..., description="Токен пользователя, имеющего право на изменение статуса проблемы")
    status: str = Field(default=..., description="Новый статус проблемы, которым необходимо заменить старый статус")

class IssueDelete(BaseModel):
    id: UUID = Field(default=..., description="ID удаляемой проблемы, выраженной в UUID")
    token: UUID = Field(default=..., description="Токен пользователя, имеющего право на удаление проблемы")

class IssuesField(BaseModel):
    type: str = Field(default=..., description="Тип возможной проблемы")

class IssuesFieldCreate(IssuesField):
    token: UUID = Field(default=..., description="Токен пользователя, имеющего право на добавление новых типов проблем")


class Request(BaseModel):
    token: UUID = Field(default=..., description="Токен предназначенный для запроса")
