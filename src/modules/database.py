from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import config_values

engine = create_engine(config_values.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()
