from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

from src.config import DB_HOST, DB_USER, DB_NAME, DB_PORT, DB_PASSWORD


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
