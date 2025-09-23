"""
Database configuration and session management
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:////Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session for FastAPI endpoints

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Base class for SQLAlchemy models (if not already defined)
class Base(DeclarativeBase):
    pass