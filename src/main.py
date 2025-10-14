import uvicorn
from fastapi import FastAPI

from db.db_models import Base
from core.config import engine, SessionDep
from api.v1 import user_router, analytics_router, transaction_router


app = FastAPI()

app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(transaction_router)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup(session: SessionDep):
    await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=True)
