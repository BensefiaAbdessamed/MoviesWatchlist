from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from contextlib import asynccontextmanager


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./watchlist.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  ,
    echo = False,
)

base = declarative_base()

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False, 
)

@asynccontextmanager
async def lifespan(_app: FastAPI)
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    yield
    await engine.dispose()