from sqlalchemy import (create_engine, MetaData, Table, Column, UUID, String, Boolean, Integer, TIMESTAMP, Float, func,
                        Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import config_values

metadata = MetaData()

engine = create_engine(
    config_values.DATABASE_URL,
    pool_size=0,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()

users = Table(
    "users", metadata,
    Column("id", UUID(), primary_key=True),
    Column("username", String(50), unique=True, nullable=False),
    Column("email", String(100), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("role", String(20), default=False),
    Column("rating", Integer(), default=0),
    Column("created_at", TIMESTAMP(), server_default=func.now(), nullable=False),
    Column("token", UUID(), nullable=False),
    Column("email_verify", Boolean(), nullable=False),
    Column("verify_token", UUID(), nullable=False)
)

issues = Table(
    "issues", metadata,
    Column("id", UUID(), primary_key=True),
    Column("user_id", UUID(), nullable=False),
    Column("type", String(50), nullable=False),
    Column("short_desc", String(200), nullable=False),
    Column("full_desc", Text(), nullable=False),
    Column("status", String(20), nullable=False),
    Column("address", String(255), nullable=False),
    Column("latitude", Float(), nullable=False),
    Column("longitude", Float(), nullable=False),
    Column("created_at", TIMESTAMP(), nullable=False),
    Column("updated_at", TIMESTAMP(), nullable=False)
)

issuesField = Table(
    "issues_field", metadata,
    Column("type", String(50), nullable=False, unique=True, primary_key=True),
)

roles = Table(
    "roles", metadata,
    Column("role", String(20), nullable=False, unique=True, primary_key=True)
)

photos = Table(
    "photos", metadata,
    Column("id", UUID(), primary_key=True, nullable=False),
    Column("issue_id", UUID(), nullable=False),
    Column("file_path", String(255), nullable=False),
    Column("uploaded_at", TIMESTAMP, nullable=False)
)

try:
    metadata.create_all(engine)
except Exception as e:
    raise ValueError("Нет подключения к базе данных...")
