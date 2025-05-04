from pydantic import BaseModel, EmailStr
from pydantic.types import UUID


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID

class UserLogin(BaseModel):
    email: EmailStr | None
    username: str | None
    password: str


# class Issue(BaseModel):
#     user_id: UUID
