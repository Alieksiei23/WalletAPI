import typing

from core.config import SessionDep
from fastapi import APIRouter, status
from services.analityc_service import AnalitycService


router = APIRouter()


@router.get("/transactions/analysis",
            response_model=typing.Optional[list] | None,
            status_code=status.HTTP_200_OK)
async def get_transaction_analysis(session: SessionDep) -> list[dict[str, typing.Any]]:
    result = await AnalitycService.get_analitycs_for_52_weeks(session)
    return result
