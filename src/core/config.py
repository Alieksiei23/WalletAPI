import typing
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_USER: str


    @property
    def url_db(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

engine = create_async_engine(settings.url_db)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> typing.AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = typing.Annotated[AsyncSession, Depends(get_async_session)]