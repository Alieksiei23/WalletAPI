import typing
from fastapi import APIRouter
from fastapi import status

from core.config import SessionDep
from services.transacriom_service import TransactionService
from api.shema.python_models import TransactionModel, RequestTransactionModel


router = APIRouter()


@router.get("/transactions",
            response_model=typing.Optional[list[TransactionModel]] | None,
            status_code=status.HTTP_200_OK)
async def get_transactions(session: SessionDep,
                           user_id: typing.Optional[int] = None,
                           ) -> typing.List[TransactionModel]:
    result = await TransactionService.get_transaction(session, user_id)
    return result


@router.post("/{user_id}/transactions",
            response_model=typing.Optional[TransactionModel] | None,
            status_code=status.HTTP_200_OK)
async def post_transaction(user_id: int, transaction: RequestTransactionModel, session: SessionDep):
    result = await TransactionService.create_transaction(user_id, transaction, session)
    return result


@router.patch("/{user_id}/transactions/{transaction_id}",
    response_model=typing.Optional[TransactionModel] | None)
async def patch_rollback_transaction(user_id: int, transaction_id: int, session: SessionDep):
    result = await TransactionService.rollback_transaction(user_id, transaction_id, session)
    return result
