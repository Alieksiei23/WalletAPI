from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette import status

from fastapi import FastAPI
from src.tasks.tasks import get_analytics_task


@pytest.mark.asyncio
async def test_get_analytics(overridden_app: FastAPI) -> None:
    with patch.object(get_analytics_task, 'send') as _:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.get("/transactions/analysis")
            assert request.status_code == status.HTTP_200_OK
            assert request.json() == {"message": "success"}
