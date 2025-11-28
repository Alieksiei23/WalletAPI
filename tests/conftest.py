from typing import Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine,)

from fastapi import FastAPI
from src.core.config import get_async_session, settings
from src.db.db_models import Base
from src.main import app


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    test_engine = create_async_engine(settings.url_test_db, echo=False,)
    test_async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db() -> AsyncSession:
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture
def overridden_app(override_get_db: Callable) -> FastAPI:
    app.dependency_overrides[get_async_session] = override_get_db
    return app
