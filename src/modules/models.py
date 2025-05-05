from sqlalchemy import Column, Integer, String, UUID, Boolean, TIMESTAMP, func
from .database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default=False)
    rating = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    token = Column(UUID, nullable=False)
    email_verify = Column(Boolean, nullable=False)
    verify_token = Column(UUID, nullable=False)


class Issue(Base):
    __tablename__ = "issues"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False)
    type = Column(String, nullable=False)
    short_desc = Column(String, nullable=False)
    full_desc = Column(String, nullable=False)
    status = Column(String, nullable=False)
    address = Column(String, nullable=False)
