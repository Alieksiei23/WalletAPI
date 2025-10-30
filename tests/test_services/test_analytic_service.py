import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.services.logic.analityc_service import AnalitycService


@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession) -> None:
    results = await AnalitycService.get_analitycs_for_52_weeks(db_session)
    assert len(results) == settings.amount_weeks
    assert "start date" in results[0]
    assert "end date" in results[0]
    assert "registered users count" in results[0]
    assert "deposit distinct users count" in results[0]
    assert "deposit amount without rollback" in results[0]
    assert "withdraw amount without rollback" in results[0]
    assert "transactions count" in results[0]
    assert "not rollbacked transactions count" in results[0]
