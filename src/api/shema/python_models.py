import typing
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr
from pydantic.v1 import root_validator

from enums.enum import CurrencyEnum, TransactionStatusEnum, UserStatusEnum


class RequestUserModel(BaseModel):
    email: EmailStr


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[Decimal] = None


class ResponseUserModel(BaseModel):
    id: typing.Optional[int]
    email: typing.Optional[str] = None
    status: typing.Optional[UserStatusEnum] = None
    created: typing.Optional[datetime] = None
    balances: typing.Optional[typing.List[ResponseUserBalanceModel]] = None


class UserModel(BaseModel):
    id: typing.Optional[int]
    email: typing.Optional[str] = None
    status: typing.Optional[UserStatusEnum] = None
    created: typing.Optional[datetime] = None


class UserBalanceModel(BaseModel):
    id: typing.Optional[int]
    user_id: typing.Optional[int] = None
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[Decimal] = None

    @root_validator(pre=True)
    def validate_not_negative(self, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "amount" in values and values.get("amount"):
            if values["amount"] < 0:
                raise ValueError("Amount cannot be negative")

        return values


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal


class TransactionModel(BaseModel):
    id: typing.Optional[int]
    user_id: typing.Optional[int] = None
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[Decimal] = None
    status: typing.Optional[TransactionStatusEnum] = None
    created: typing.Optional[datetime] = None
