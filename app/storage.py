from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config_prod import settings
from app.db import Base

engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=settings.database.pool_pre_ping,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
