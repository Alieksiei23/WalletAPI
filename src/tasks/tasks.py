import asyncio

from src.core.config import async_session_maker
from src.core.dramatic_settings import dramatiq
from src.services.logic.analityc_service import AnalitycService


@dramatiq.actor
def get_analitycs_task() -> None:

    async def run_task() -> None:
        async with async_session_maker() as session:
            result = await AnalitycService.get_analitycs_for_52_weeks(session)
            print(result)

    asyncio.run(run_task())
