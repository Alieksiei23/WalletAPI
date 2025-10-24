from typing import Optional

from fastapi import status
from src.core.exceptions.exceptions import (
    BadRequestDataException, NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException, TransactionNotExistsException,
    UserAlreadyActiveException, UserAlreadyBlockedException,
    UserNotExistsException,)
from src.db.db_models import Transaction, User


class CheckData:

    @staticmethod
    def validate_positive_number(*args: int) -> None:
        for arg in args:
            if arg <= 0:
                raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              detail="Unprocessable data in request")

    @staticmethod
    def check_positive_balance(amount: int) -> None:
        if amount < 0:
            raise NegativeBalanceException(status_code=status.HTTP_400_BAD_REQUEST,
                                           detail=f"Negative balance: {amount}",)

    @staticmethod
    def validate_status(user_id: int, stat: str) -> None:
        if stat == "BLOCKED":
            raise UserAlreadyBlockedException(status_code=status.HTTP_400_BAD_REQUEST,
                                              detail="User with id=`{0}` is blocked".format(user_id))

    @staticmethod
    def check_update_status(user_status: str, user_update_status: str, user_id: int) -> None:
        if user_status == "BLOCKED" and user_update_status == "BLOCKED":
            raise UserAlreadyBlockedException(status_code=status.HTTP_400_BAD_REQUEST,
                                              detail="User with id=`{0}` is already blocked".format(user_id))
        if user_status == "ACTIVE" and user_update_status == "ACTIVE":
            raise UserAlreadyActiveException(status_code=status.HTTP_400_BAD_REQUEST,
                                             detail="User with id=`{0}` is already active".format(user_id))

    @staticmethod
    def check_rollback_trans(transaction_id: int, stat: str) -> None:
        if stat == "ROLLBACKED":
            raise TransactionAlreadyRollbackedException(status_code=status.HTTP_400_BAD_REQUEST,
                                                        detail="Transaction with id=`{0}` is already rollbacked"
                                                        .format(transaction_id))

    @staticmethod
    def check_exist_user(user_id: int, request: Optional[User]) -> None:
        if not request:
            raise UserNotExistsException(status_code=status.HTTP_404_NOT_FOUND,
                                         detail="User with id=`{0}` does not exist".format(user_id))

    @staticmethod
    def check_exist_trans(transaction_id: int, request: Optional[Transaction]) -> None:
        if not request:
            raise TransactionNotExistsException(status_code=status.HTTP_400_BAD_REQUEST,
                                                detail="Transaction with id=`{0}` does not exist"
                                                .format(transaction_id))

    @staticmethod
    def check_amount_trans(amount: int) -> None:
        if amount == 0:
            raise BadRequestDataException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail="Transaction can not have zero amount")

    @staticmethod
    def chek_owner_trans(transaction_user_id: int, user_id: int, transaction_id: int) -> None:
        if transaction_user_id != user_id:
            raise TransactionDoesNotBelongToUserException(status_code=status.HTTP_400_BAD_REQUEST,
                                                          detail="Transaction with id=`{0}` does not belong to user with id=`{1}`"
                                                          .format(transaction_id, user_id))
