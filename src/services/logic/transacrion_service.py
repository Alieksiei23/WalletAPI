import typing
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schema.python_models import (RequestTransactionModel,
                                          TransactionModel,)
from src.db.db_models import Transaction, User, UserBalance
from src.services.validate_data_service import CheckData


class TransactionService:

    @staticmethod
    async def get_transaction(session: AsyncSession,
                              user_id: typing.Optional[int] = None
                              ) -> typing.List[TransactionModel]:
        query = select(Transaction).order_by(Transaction.created.desc())
        if user_id:
            query = query.where(Transaction.user_id == user_id)

        transactions = await session.execute(query)
        transactions_rows = transactions.scalars()
        return [TransactionModel.model_validate(t) for t in transactions_rows]

    @staticmethod
    async def create_transaction(user_id: int,
                                 transaction: RequestTransactionModel,
                                 session: AsyncSession) -> typing.Dict[str, str]:
        CheckData.validate_positive_number(user_id)
        CheckData.check_amount_trans(transaction.amount)

        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()
        CheckData.check_exist_user(user_id, db_user)
        CheckData.validate_status(user_id, db_user.status)

        db_user_balance_row = await session.execute(select(UserBalance)
                                                    .where((UserBalance.user_id == user_id)
                                                           & (UserBalance.currency == transaction.currency)))
        db_user_balance = db_user_balance_row.scalar()
        if db_user_balance:
            result_amount = db_user_balance.amount + transaction.amount
            CheckData.check_positive_balance(result_amount)

            await session.execute(update(UserBalance)
                                  .values(**{"amount": result_amount})
                                  .where(UserBalance.id == db_user_balance.id))
            await session.execute(
                insert(Transaction).values(
                    **{"user_id": db_user.id,
                       "currency": transaction.currency,
                       "amount": transaction.amount,
                       "status": "PROCESSED",
                       "created": datetime.utcnow(),
                       }
                )
            )
            await session.commit()
        return {"message": "Transaction created"}

    @staticmethod
    async def rollback_transaction(user_id: int,
                                   transaction_id: int,
                                   session: AsyncSession
                                   ) -> typing.Optional[dict[str, str]]:
        CheckData.validate_positive_number(transaction_id, user_id)

        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()
        CheckData.check_exist_user(user_id, db_user)
        CheckData.validate_status(user_id, db_user.status)

        db_transaction_row = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
        db_transaction = db_transaction_row.scalar()
        CheckData.check_exist_trans(transaction_id, db_transaction)
        CheckData.chek_owner_trans(db_transaction.user_id, user_id, transaction_id)
        CheckData.check_rollback_trans(transaction_id, db_transaction.status)
        db_user_balance_row = await session.execute(select(UserBalance)
                                                    .where((UserBalance.user_id == user_id)
                                                           & (UserBalance.currency == db_transaction.currency)))
        db_user_balance = db_user_balance_row.scalar()
        if db_user_balance:
            new_amount = db_user_balance.amount
            if db_transaction.amount < 0:
                new_amount += abs(db_transaction.amount)
            else:
                new_amount -= db_transaction.amount
            CheckData.check_positive_balance(new_amount)

            await session.execute(update(UserBalance)
                                  .values(**{"amount": new_amount})
                                  .where((UserBalance.id == db_user_balance.id)
                                         & (UserBalance.currency == db_transaction.currency)))
            await session.commit()
            await session.execute(update(Transaction)
                                  .values(**{"status": "ROLLBACKED"})
                                  .where(Transaction.id == transaction_id))
            await session.commit()
        return {'message': 'Transaction rolled back'}
