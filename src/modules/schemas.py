from pydantic import BaseModel, EmailStr
from pydantic.types import UUID


# Пользовательские классы
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    role: str
    token: UUID
    email_verify: bool

class UserLogin(BaseModel):
    email: EmailStr | None
    username: str | None
    password: str

class UserDelete(BaseModel):
    id: UUID
    token: UUID

class VerifyEmail(BaseModel):
    token: UUID

class ChangePassword(BaseModel):
    token: UUID
    old_password: str
    new_password: str

class ChangeRole(BaseModel):
    user_id: UUID
    token: UUID
    role: str

class RoleCreate(BaseModel):
    token: UUID
    role: str

class Role(BaseModel):
    role: str


# Классы проблем
class IssueCreate(BaseModel):
    token: UUID
    type: str
    short_desc: str
    full_desc: str
    address: str

class Issue(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    type: str
    short_desc: str
    full_desc: str
    address: str

class IssueUpdate(BaseModel):
    id: UUID
    token: UUID
    status: str

class IssueDelete(BaseModel):
    id: UUID
    token: UUID

class IssuesField(BaseModel):
    type: str

class IssuesFieldCreate(IssuesField):
    token: UUID
