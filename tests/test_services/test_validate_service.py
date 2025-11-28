from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest

from src.core.exceptions.exceptions import (
    BadRequestDataException, NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException, TransactionNotExistsException,
    UserAlreadyActiveException, UserAlreadyBlockedException,
    UserNotExistsException,)
from src.services.validate_data_service import CheckData


class TestCheckData:

    @pytest.mark.parametrize(
        "number, expectation", [
            (1, does_not_raise()),
            (32145, does_not_raise()),
            (0, pytest.raises(BadRequestDataException)),
            (-3125, pytest.raises(BadRequestDataException)),
        ]
    )
    def test_validate_positive_number(self, number: int, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.validate_positive_number(number) is None

    @pytest.mark.parametrize(
        "number, expectation", [
            (653, does_not_raise()),
            (0, does_not_raise()),
            (-3125, pytest.raises(NegativeBalanceException)),
        ]
    )
    def test_check_positive_balance(self, number: int, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_positive_balance(number) is None

    @pytest.mark.parametrize(
        "user_id, status, expectation", [
            (1, "BLOCKED", pytest.raises(UserAlreadyBlockedException)),
            (1, "ACTIVE", does_not_raise()),
        ]
    )
    def test_validate_status(self, user_id: int, status: str, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.validate_status(user_id, status) is None

    @pytest.mark.parametrize(
        "user_status, update_status, user_id, expectation", [
            ("BLOCKED", "BLOCKED", 1, pytest.raises(UserAlreadyBlockedException)),
            ("ACTIVE", "ACTIVE", 1, pytest.raises(UserAlreadyActiveException)),
            ("ACTIVE", "BLOCKED", 1, does_not_raise()),
        ]
    )
    def test_check_update_status(self,
                                 user_status: str,
                                 update_status: str,
                                 user_id: int,
                                 expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_update_status(user_status, update_status, user_id) is None

    @pytest.mark.parametrize(
        "trans_id, status, expectation", [
            (1, "ROLLBACKED", pytest.raises(TransactionAlreadyRollbackedException)),
            (1, "PROCESSED", does_not_raise()),
        ]
    )
    def test_check_rollback_trans(self, trans_id: int, status: str, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_rollback_trans(trans_id, status) is None

    @pytest.mark.parametrize(
        "user_id, data, expectation", [
            (1, [], pytest.raises(UserNotExistsException)),
            (1, None, pytest.raises(UserNotExistsException)),
            (1, ["User"], does_not_raise()),
        ]
    )
    def test_check_exist_user(self, user_id: int, data: Any, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_exist_user(user_id, data) is None

    @pytest.mark.parametrize(
        "trans_id, data, expectation", [
            (1, [], pytest.raises(TransactionNotExistsException)),
            (1, None, pytest.raises(TransactionNotExistsException)),
            (1, ["Trans"], does_not_raise()),
        ]
    )
    def test_check_exist_trans(self, trans_id: int, data: Any, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_exist_trans(trans_id, data) is None

    @pytest.mark.parametrize(
        "amount, expectation", [
            (123, does_not_raise()),
            (0, pytest.raises(BadRequestDataException)),
            (-123, does_not_raise()),
        ]
    )
    def test_check_amount_trans(self, amount: int, expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.check_amount_trans(amount) is None

    @pytest.mark.parametrize(
        "transaction_user_id, user_id, id, expectation", [
            (1, 1, 5, does_not_raise()),
            (33, 52, 5, pytest.raises(TransactionDoesNotBelongToUserException)),
            (321, 321, 5, does_not_raise()),
        ]
    )
    def test_chek_owner_trans(self,
                              transaction_user_id: int,
                              user_id: int,
                              id: int,
                              expectation: AbstractContextManager[Any]) -> None:
        with expectation:
            assert CheckData.chek_owner_trans(transaction_user_id, user_id, id) is None
