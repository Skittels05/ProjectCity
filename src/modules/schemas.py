from pydantic import BaseModel, EmailStr
from pydantic.types import UUID


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


class VerifyEmail(BaseModel):
    token: str


class IssueCreate(BaseModel):
    user_id: UUID
    type: str
    short_desc: str
    full_desc: str
    address: str

class Issue(IssueCreate):
    id: UUID
    status: str

class IssueUpdate(BaseModel):
    id: UUID
    token: UUID
    status: str

class IssueDelete(BaseModel):
    id: UUID
    token: UUID
