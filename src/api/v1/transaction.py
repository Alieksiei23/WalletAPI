import typing

from fastapi import APIRouter, status
from src.api.shema.python_models import (RequestTransactionModel,
                                         TransactionModel,)
from src.core.config import SessionDep
from src.services.transacrion_service import TransactionService


router = APIRouter()


@router.get("/transactions",
            response_model=typing.List[TransactionModel],
            status_code=status.HTTP_200_OK)
async def get_transactions(session: SessionDep,
                           user_id: typing.Optional[int] = None,
                           ) -> typing.List[TransactionModel]:
    result = await TransactionService.get_transaction(session, user_id)
    return result


@router.post("/{user_id}/transactions",
             response_model=typing.Dict[str, str],
             status_code=status.HTTP_200_OK)
async def post_transaction(user_id: int, transaction: RequestTransactionModel, session: SessionDep) -> typing.Dict[str, str]:
    result = await TransactionService.create_transaction(user_id, transaction, session)
    return result


@router.patch("/{user_id}/transactions/{transaction_id}",
              response_model=typing.Optional[dict[str, str]])
async def patch_rollback_transaction(user_id: int, transaction_id: int, session: SessionDep) -> typing.Optional[dict[str, str]]:
    result = await TransactionService.rollback_transaction(user_id, transaction_id, session)
    return result
