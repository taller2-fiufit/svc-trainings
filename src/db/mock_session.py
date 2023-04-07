from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import TEST_DATABASE_URL


engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    engine, autocommit=False, autoflush=False, expire_on_commit=False
)
