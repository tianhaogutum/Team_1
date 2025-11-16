"""
Database configuration and session management using SQLAlchemy.
"""
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Global engine and session factory
_engine = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_database_url(settings: Settings) -> str:
    """
    Construct the database URL from settings.
    
    For Supabase, the DATABASE_URL format is:
    postgresql+asyncpg://postgres:[password]@[host]:[port]/postgres
    
    Automatically converts postgresql:// to postgresql+asyncpg:// if needed.
    """
    url = settings.database_url.get_secret_value()
    
    # Ensure we're using asyncpg driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        raise ValueError(
            f"Invalid DATABASE_URL format. Expected 'postgresql+asyncpg://' or 'postgresql://', "
            f"got: {url[:30]}..."
        )
    
    return url


def init_db(settings: Settings | None = None) -> None:
    """
    Initialize the database engine and session factory.
    
    Parameters
    ----------
    settings:
        Optional Settings instance; if omitted the global application settings are used.
    """
    global _engine, _async_session_maker
    
    if settings is None:
        settings = get_settings()
    
    database_url = get_database_url(settings)
    
    # Create async engine
    _engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        future=True,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    )
    
    # Create session factory
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def close_db() -> None:
    """Close the database engine."""
    global _engine
    if _engine:
        await _engine.dispose()


@asynccontextmanager
async def get_db() -> AsyncSession:
    """
    Dependency for getting a database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _async_session_maker is None:
        init_db()
    
    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Get a database session (alternative to context manager).
    Remember to close the session after use.
    """
    if _async_session_maker is None:
        init_db()
    
    return _async_session_maker()

