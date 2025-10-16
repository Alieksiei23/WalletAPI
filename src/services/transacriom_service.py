import typing
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.shema.python_models import (CurrencyEnum, RequestTransactionModel,
                                     TransactionModel, TransactionStatusEnum,)
from core.exceptions.exceptions import (
    BadRequestDataException, CreateTransactionForBlockedUserException,
    NegativeBalanceException, TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException, TransactionNotExistsException,
    UpdateTransactionForBlockedUserException, UserNotExistsException,)
from db.db_models import Transaction, User, UserBalance
from fastapi import status


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
        results = []
        for t in transactions_rows:
            result = TransactionModel(
                **{
                    "id": t.id,
                    "user_id": t.user_id,
                    "currency": CurrencyEnum(t.currency),
                    "amount": t.amount,
                    "status": TransactionStatusEnum(t.status),
                    "created": t.created,
                }
            )
            results.append(result)
        return results

    @staticmethod
    async def create_transaction(user_id: int,
                                 transaction: RequestTransactionModel,
                                 session: AsyncSession) -> typing.Dict[str, str]:
        if user_id <= 0:
            raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail="Unprocessable data in request")
        if transaction.amount == 0:
            raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail="Transaction can not have zero amount")

        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()

        if not db_user:
            raise UserNotExistsException(status_code=status.HTTP_404_NOT_FOUND,
                                         detail="User with id=`{0}` does not exist".format(user_id))
        if db_user.status != "ACTIVE":
            raise CreateTransactionForBlockedUserException(status_code=status.HTTP_404_NOT_FOUND,
                                                           detail="User with id=`{0}` is blocked".format(user_id))
        db_user_balance_row = await session.execute(select(UserBalance).where((UserBalance.user_id == user_id)
                                                                              & (UserBalance.currency == transaction.currency)))
        db_user_balance = db_user_balance_row.scalar()
        if db_user_balance:
            if db_user_balance.amount + transaction.amount < 0:
                raise NegativeBalanceException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Negative balance"
                )
            result_amount = db_user_balance.amount + transaction.amount
            await session.execute(update(UserBalance)
                                  .values(**{"amount": result_amount})
                                  .where(UserBalance.id == db_user_balance.id))
            await session.commit()
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
                                   ) -> typing.Optional[TransactionModel]:
        if user_id <= 0 or transaction_id <= 0:
            raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail="Unprocessable data in request")
        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()
        if not db_user:
            raise UserNotExistsException(status_code=status.HTTP_404_NOT_FOUND,
                                         detail="User with id=`{0}` does not exist".format(user_id))
        db_transaction_row = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
        db_transaction = db_transaction_row.scalar()
        if not db_transaction:
            raise TransactionNotExistsException(status_code=status.HTTP_400_BAD_REQUEST,
                                                detail="Transaction with id=`{0}` does not exist"
                                                .format(transaction_id)
                                                )
        if db_transaction.user_id != db_user.id:
            raise TransactionDoesNotBelongToUserException(status_code=status.HTTP_400_BAD_REQUEST,
                                                          detail="Transaction with id=`{0}` does not belong to user with id=`{1}`"
                                                          .format(transaction_id, user_id)
                                                          )
        if db_transaction.status == "ROLLBACKED":
            raise TransactionAlreadyRollbackedException(status_code=status.HTTP_400_BAD_REQUEST,
                                                        detail="Transaction with id=`{0}` is already rollbacked"
                                                        .format(transaction_id)
                                                        )
        if db_user.status == "BLOCKED":
            raise UpdateTransactionForBlockedUserException(status_code=status.HTTP_400_BAD_REQUEST,
                                                           detail="User with id=`{0}` is blocked".format(user_id))

        db_user_balance_row = await session.execute(
                                                select(UserBalance)
                                                .where(
                                                    (UserBalance.user_id == user_id)
                                                    & (UserBalance.currency == db_transaction.currency)
                                                )
                                            )
        db_user_balance = db_user_balance_row.scalar()
        if db_user_balance:
            new_amount = db_user_balance.amount
            if db_transaction.amount < 0:
                new_amount += abs(db_transaction.amount)
            else:
                new_amount -= db_transaction.amount
            if new_amount < 0:
                raise NegativeBalanceException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Negative balance: {new_amount}",
                )
            await session.execute(update(UserBalance)
                                  .values(**{"amount": new_amount})
                                  .where((UserBalance.id == db_user_balance.id)
                                         & (UserBalance.currency == db_transaction.currency))
                                  )
            await session.commit()
            await session.execute(
                                  update(Transaction)
                                  .values(**{"status": "ROLLBACKED"})
                                  .where(Transaction.id == transaction_id)
                                   )
            await session.commit()
