import typing
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.shema.python_models import (CurrencyEnum, RequestUserUpdateModel,
                                     ResponseUserModel, UserModel,
                                     UserStatusEnum,)
from core.config import get_async_session
from core.exceptions.exceptions import (BadRequestDataException,
                                        UserAlreadyActiveException,
                                        UserAlreadyBlockedException,
                                        UserAlreadyExistsException,
                                        UserNotExistsException,)
from db.db_models import User, UserBalance
from fastapi import Depends, status


class UserService:

    @staticmethod
    async def get_users(user_id: typing.Optional[int] = None,
                        email: typing.Optional[str] = None,
                        user_status: typing.Optional[str] = None,
                        session: AsyncSession = Depends(get_async_session),
                        ) -> typing.List[ResponseUserModel]:
        query = select(User).order_by(User.created.desc())

        if user_id is not None:
            query = query.where(User.id == user_id)
        if email is not None:
            query = query.where(User.email == email)
        if user_status is not None:
            query = query.where(User.status == user_status)

        users = await session.execute(query)
        users_rows = users.scalars()
        results = []
        for user in users_rows:
            result = ResponseUserModel(id=user.id, email=user.email,
                                       status=UserStatusEnum(user.status), created=user.created)
            balances = await session.execute(select(UserBalance).where(UserBalance.user_id == user.id))
            balances_row = balances.scalars()
            balances_sorted = sorted(
                [{"currency": b.currency, "amount": b.amount} for b in balances_row],
                key=lambda x: x["amount"],
            )
            result.balances = balances_sorted
            results.append(result)
        return sorted(results, key=lambda x: x.created)

    @staticmethod
    async def register_user(user: RequestUserUpdateModel, session: AsyncSession) -> typing.Optional[UserModel]:
        db_user = await session.execute(select(User).where(User.email == user.email))
        if db_user.scalar():
            raise UserAlreadyExistsException(status_code=status.HTTP_409_CONFLICT,
                                             detail="User with email=`{0}` already exists".format(user.email))
        db_user = User(email=user.email, status="ACTIVE", created=datetime.utcnow())
        session.add(db_user)
        await session.commit()
        currencies = list({str(x) for x in CurrencyEnum})
        for currency in currencies:
            user_balance = UserBalance(user_id=db_user.id,
                                       currency=currency,
                                       amount=0,
                                       created=datetime.utcnow())
            session.add(user_balance)
            await session.commit()
        result = await session.execute(select(User).where(User.email == user.email))
        result_row = result.scalar()
        if result_row:
            result = UserModel(id=result_row.id,
                               email=result_row.email,
                               status=UserStatusEnum(result_row.status),
                               created=result_row.created)

        return result

    @staticmethod
    async def update_user_status(
        user_id: int, user: RequestUserUpdateModel, session: AsyncSession
    ) -> UserModel:
        if user_id <= 0:
            raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail="Unprocessable data in request")
        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()

        if not db_user:
            raise UserNotExistsException(status_code=status.HTTP_404_NOT_FOUND,
                                         detail="User with id=`{0}` does not exist".format(user_id))
        if db_user.status == "BLOCKED" and user.status == "BLOCKED":
            raise UserAlreadyBlockedException(status_code=status.HTTP_400_BAD_REQUEST,
                                              detail="User with id=`{0}` is already blocked".format(user_id))
        if db_user.status == "ACTIVE" and user.status == "ACTIVE":
            raise UserAlreadyActiveException(status_code=status.HTTP_400_BAD_REQUEST,
                                             detail="User with id=`{0}` is already active".format(user_id))

        await session.execute(update(User).values(**{"status": user.status}).where(User.id == user_id))
        await session.commit()
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalar()
        result = UserModel(id=user.id,
                           email=user.email,
                           status=UserStatusEnum(user.status),
                           created=user.created)
        return result
