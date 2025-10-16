import uvicorn

from api.v1 import analytics_router, transaction_router, user_router
from core.config import engine
from db.db_models import Base
from fastapi import FastAPI


app = FastAPI()

app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(transaction_router)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup() -> None:
    await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=True)
