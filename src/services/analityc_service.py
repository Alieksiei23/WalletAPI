from datetime import datetime, timedelta

from db.queries import (
    get_registered_users_count,
    get_registered_and_deposit_users_count,
    get_registered_and_not_rollbacked_deposit_users_count,
    get_not_rollbacked_deposit_amount,
    get_not_rollbacked_withdraw_amount,
    get_transactions_count,
    get_not_rollbacked_transactions_count,
)


class AnalitycService:
    @staticmethod
    async def get_analitycs_for_52_weeks(session):
        dt_gt = datetime.utcnow().date() - timedelta(weeks=1) + timedelta(days=1)
        dt_lt = datetime.utcnow().date()
        results = []
        amount_weeks = 52
        for week in range(amount_weeks):
            registered_users_count = await get_registered_users_count(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            registered_and_deposit_users_count = (
                await get_registered_and_deposit_users_count(
                    session, dt_gt=dt_gt, dt_lt=dt_lt
                )
            )
            registered_and_not_rollbacked_deposit_users_count = (
                await get_registered_and_not_rollbacked_deposit_users_count(
                    session, dt_gt=dt_gt, dt_lt=dt_lt
                )
            )
            not_rollbacked_deposit_amount = await get_not_rollbacked_deposit_amount(
                session, dt_gt=dt_gt, dt_lt=dt_lt
            )
            not_rollbacked_withdraw_amount = await get_not_rollbacked_withdraw_amount(
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
                "start_date": dt_gt,
                "end_date": dt_lt,
                "registered_users_count": registered_users_count,
                "registered_and_deposit_users_count": registered_and_deposit_users_count,
                "registered_and_not_rollbacked_deposit_users_count": registered_and_not_rollbacked_deposit_users_count,
                "not_rollbacked_deposit_amount": not_rollbacked_deposit_amount,
                "not_rollbacked_withdraw_amount": not_rollbacked_withdraw_amount,
                "transactions_count": transactions_count,
                "not_rollbacked_transactions_count": not_rollbacked_transactions_count,
            }
            for field in (
                "registered_users_count",
                "registered_and_deposit_users_count",
                "registered_and_not_rollbacked_deposit_users_count",
                "not_rollbacked_deposit_amount",
                "not_rollbacked_withdraw_amount",
                "transactions_count",
                "not_rollbacked_transactions_count",
            ):
                if result[field] > 0:
                    results.append(result)
                    break
            dt_gt -= timedelta(weeks=1)
            dt_lt -= timedelta(weeks=1)
        return results
