import typing
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import Depends, status
from src.api.schema.python_models import (CurrencyEnum, RequestUserModel,
                                          RequestUserUpdateModel,
                                          ResponseUserModel, UserModel,
                                          UserStatusEnum,)
from src.core.config import get_async_session
from src.core.exceptions.exceptions import UserAlreadyExistsException
from src.db.db_models import User, UserBalance
from src.services.validate_data_service import CheckData


class UserService:

    @staticmethod
    async def get_users(user_id: typing.Optional[int] = None,
                        email: typing.Optional[str] = None,
                        user_status: typing.Optional[str] = None,
                        session: AsyncSession = Depends(get_async_session),
                        ) -> typing.List[ResponseUserModel]:
        query = select(User).options(selectinload(User.user_balance))

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
            balances_sorted = sorted(
                [{"currency": balance.currency, "amount": balance.amount} for balance in user.user_balance],
                key=lambda x: x["amount"],
            )
            result.balances = balances_sorted
            results.append(result)
        return results

    @staticmethod
    async def register_user(user: RequestUserModel, session: AsyncSession) -> typing.Optional[UserModel]:
        try:
            db_user = User(email=user.email, status="ACTIVE", created=datetime.now())
            session.add(db_user)
            await session.commit()
        except IntegrityError:
            raise UserAlreadyExistsException(status_code=status.HTTP_409_CONFLICT,
                                             detail="User with email=`{0}` already exists".format(user.email))
        user_balances = []
        for currency in CurrencyEnum:
            user_balances.append(UserBalance(user_id=db_user.id,
                                             currency=currency,
                                             amount=0,
                                             created=datetime.now()))
        session.add_all(user_balances)
        await session.commit()
        result = UserModel(id=db_user.id,
                           email=db_user.email,
                           status=UserStatusEnum(db_user.status),
                           created=db_user.created)
        return result

    @staticmethod
    async def update_user_status(user_id: int,
                                 user: RequestUserUpdateModel,
                                 session: AsyncSession
                                 ) -> UserModel:
        CheckData.validate_positive_number(user_id)

        db_user_row = await session.execute(select(User).where(User.id == user_id))
        db_user = db_user_row.scalar()

        CheckData.check_exist_user(user_id, db_user)
        CheckData.check_update_status(db_user.status, user.status, user_id)

        await session.execute(update(User).values(**{"status": user.status}).where(User.id == user_id))
        await session.commit()
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalar()
        result = UserModel(id=user.id,
                           email=user.email,
                           status=UserStatusEnum(user.status),
                           created=user.created)
        return result
