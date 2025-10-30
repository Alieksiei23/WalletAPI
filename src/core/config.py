import typing
from datetime import date, datetime, timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine,)

from fastapi import Depends


class Settings(BaseSettings):
    DB_NAME: str
    TEST_DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_USER: str
    RM_HOST: str
    RM_PORT: int
    RM_USER: str
    RM_PASS: str
    amount_weeks: int = 52
    start_day: date = datetime.now().date()
    week_ago: date = datetime.now().date() - timedelta(days=6)

    @property
    def url_db(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def url_test_db(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"

    @property
    def url_rm(self) -> str:
        return f"amqp://{self.RM_USER}:{self.RM_PASS}@{self.RM_HOST}:{self.RM_PORT}/"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

engine = create_async_engine(settings.url_db)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> typing.AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = typing.Annotated[AsyncSession, Depends(get_async_session)]
