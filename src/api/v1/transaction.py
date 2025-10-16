import typing

from api.shema.python_models import RequestTransactionModel, TransactionModel
from core.config import SessionDep
from fastapi import APIRouter, status
from services.transacriom_service import TransactionService


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
              response_model=typing.Optional[TransactionModel])
async def patch_rollback_transaction(user_id: int, transaction_id: int, session: SessionDep) -> typing.Optional[TransactionModel]:
    result = await TransactionService.rollback_transaction(user_id, transaction_id, session)
    return result
