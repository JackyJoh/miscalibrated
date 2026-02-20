"""
app/db/session.py — Async SQLAlchemy database session setup.

We use async SQLAlchemy so database queries don't block FastAPI's event loop.
This is important for an API that handles many concurrent requests.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ─── Engine ──────────────────────────────────────────────────────────────────
# The engine manages the underlying connection pool to PostgreSQL.
# pool_pre_ping=True checks that connections are alive before using them
# (prevents "connection was closed" errors after idle periods).
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=(settings.environment == "development"),  # Log SQL in dev mode
)


# ─── Session Factory ─────────────────────────────────────────────────────────
# AsyncSessionLocal is a factory that creates new AsyncSession instances.
# expire_on_commit=False means ORM objects stay usable after commit
# (important for async code where you can't lazily reload attributes).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── Base Model ──────────────────────────────────────────────────────────────
# All ORM models inherit from this Base. SQLAlchemy uses it to track
# all mapped tables for migrations and schema generation.
class Base(DeclarativeBase):
    pass


# ─── Dependency ──────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in a route:
        @router.get("/markets")
        async def list_markets(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Market))
            ...

    The 'async with' ensures the session is properly closed after each request,
    even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        yield session
