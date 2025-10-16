from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import (get_deposit_amount_without_rollback,
                        get_deposit_distinct_users_count,
                        get_not_rollbacked_transactions_count,
                        get_registered_users_count, get_transactions_count,
                        get_withdraw_amount_without_rollback,)


class AnalitycService:
    @staticmethod
    async def get_analitycs_for_52_weeks(session: AsyncSession) -> list[dict[str, Any]]:
        dt_gt = datetime.utcnow().date() - timedelta(days=6)
        dt_lt = datetime.utcnow().date()
        results = []
        amount_weeks = 52
        for week in range(amount_weeks):
            registered_users_count = await get_registered_users_count(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            deposit_distinct_users_count = (
                await get_deposit_distinct_users_count(
                    session, dt_gt=dt_gt, dt_lt=dt_lt
                )
            )
            deposit_amount_without_rollback = await get_deposit_amount_without_rollback(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            withdraw_amount_without_rollback = await get_withdraw_amount_without_rollback(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            transactions_count = await get_transactions_count(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            not_rollbacked_transactions_count = (
                await get_not_rollbacked_transactions_count(
                    session, dt_gt=dt_gt, dt_lt=dt_lt
                )
            )
            result = {
                "start date": dt_gt,
                "end date": dt_lt,
                "registered users count": registered_users_count,
                "deposit distinct users count": deposit_distinct_users_count,
                "deposit amount without rollback": deposit_amount_without_rollback,
                "withdraw amount without rollback": withdraw_amount_without_rollback,
                "transactions count": transactions_count,
                "not rollbacked transactions count": not_rollbacked_transactions_count,
            }
            results.append(result)
            dt_gt -= timedelta(weeks=1)
            dt_lt -= timedelta(weeks=1)
        return results
