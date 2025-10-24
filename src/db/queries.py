from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schema.python_models import CurrencyEnum
from src.db.db_models import Transaction, User
from src.enums.enum import TransactionStatusEnum


EXCHANGE_RATES_TO_USD = {
    CurrencyEnum.USD: 1,
    CurrencyEnum.EUR: 0.9342,
    CurrencyEnum.AUD: 0.5447,
    CurrencyEnum.CAD: 0.6162,
    CurrencyEnum.ARS: 0.0009,
    CurrencyEnum.PLN: 0.2343,
    CurrencyEnum.BTC: 100000.0,
    CurrencyEnum.ETH: 3557.3476,
    CurrencyEnum.DOGE: 0.3627,
    CurrencyEnum.USDT: 0.9709,
}


async def get_registered_users_count(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(User).where((func.date(User.created) >= dt_gt) & (func.date(User.created) <= dt_lt))
    registered_users = await session.execute(query)
    rows = registered_users.fetchall()
    return len(rows)


async def get_deposit_distinct_users_count(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(Transaction.user_id).where((func.date(Transaction.created) >= dt_gt)
                                              & (func.date(Transaction.created) <= dt_lt)
                                              & (Transaction.amount > 0)
                                              ).distinct()
    registered_users = await session.execute(query)
    result = registered_users.scalars()
    return len(list(result))


async def get_deposit_amount_without_rollback(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(Transaction).where((func.date(Transaction.created) >= dt_gt)
                                      & (func.date(Transaction.created) <= dt_lt)
                                      & (Transaction.amount > 0)
                                      & (Transaction.status == TransactionStatusEnum.processed.value)
                                      )
    transactions = await session.execute(query)
    transactions_rows = transactions.scalars()
    result = sum([trans.amount * Decimal(EXCHANGE_RATES_TO_USD[trans.currency]) for trans in transactions_rows])
    return result


async def get_withdraw_amount_without_rollback(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(Transaction).where((func.date(Transaction.created) >= dt_gt)
                                      & (func.date(Transaction.created) <= dt_lt)
                                      & (Transaction.amount < 0)
                                      & (Transaction.status == TransactionStatusEnum.processed.value)
                                      )
    transactions = await session.execute(query)
    transactions_rows = transactions.scalars()
    result = sum([trans.amount * Decimal(EXCHANGE_RATES_TO_USD[trans.currency]) for trans in transactions_rows])
    return result


async def get_transactions_count(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(Transaction).where((func.date(Transaction.created) >= dt_gt) & (func.date(Transaction.created) <= dt_lt))
    transactions = await session.execute(query)
    transactions_rows = transactions.fetchall()
    return len(transactions_rows)


async def get_not_rollbacked_transactions_count(session: AsyncSession, dt_gt: date, dt_lt: date) -> int:
    query = select(Transaction).where((func.date(Transaction.created) >= dt_gt)
                                      & (func.date(Transaction.created) <= dt_lt)
                                      & (Transaction.status == TransactionStatusEnum.processed.value)
                                      )
    transactions = await session.execute(query)
    transactions_rows = transactions.fetchall()
    return len(transactions_rows)
