from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.v1 import analytics_router, transaction_router, user_router
from src.core.config import engine
from src.db.db_models import Base


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(transaction_router)
