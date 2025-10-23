from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.queries import (get_deposit_amount_without_rollback,
                            get_deposit_distinct_users_count,
                            get_not_rollbacked_transactions_count,
                            get_registered_users_count, get_transactions_count,
                            get_withdraw_amount_without_rollback,)


class AnalitycService:
    @staticmethod
    async def get_analitycs_for_52_weeks(session: AsyncSession) -> list[dict[str, Any]]:
        dt_lt = settings.start_day
        dt_gt = settings.week_ago
        amount_weeks = settings.amount_weeks
        results = []
        for week in range(amount_weeks):
            result = {
                "start date": dt_gt,
                "end date": dt_lt,
                "registered users count": await get_registered_users_count(session, dt_gt=dt_gt, dt_lt=dt_lt),
                "deposit distinct users count": await get_deposit_distinct_users_count(session, dt_gt=dt_gt, dt_lt=dt_lt),
                "deposit amount without rollback": await get_deposit_amount_without_rollback(session, dt_gt=dt_gt, dt_lt=dt_lt),
                "withdraw amount without rollback": await get_withdraw_amount_without_rollback(session, dt_gt=dt_gt, dt_lt=dt_lt),
                "transactions count": await get_transactions_count(session, dt_gt=dt_gt, dt_lt=dt_lt),
                "not rollbacked transactions count": await get_not_rollbacked_transactions_count(session, dt_gt=dt_gt, dt_lt=dt_lt),
            }
            results.append(result)
            dt_gt -= timedelta(weeks=1)
            dt_lt -= timedelta(weeks=1)
        return results
