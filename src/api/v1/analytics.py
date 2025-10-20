from fastapi import APIRouter, status
from src.tasks.tasks import get_analitycs_task


router = APIRouter()


@router.get("/transactions/analysis",
            response_model=dict[str, str],
            status_code=status.HTTP_200_OK)
async def get_transaction_analysis() -> dict[str, str]:
    get_analitycs_task.send()
    return {"message": "success"}
