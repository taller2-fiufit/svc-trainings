from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import SQLALCHEMY_DATABASE_URL


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False)
