import pytest
from httpx import ASGITransport, AsyncClient
from starlette import status

from fastapi import FastAPI


class TestTransAPI:

    @pytest.mark.asyncio
    async def test_get_transaction(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            response = await client.get("/transactions")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_transaction_by_user_id(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_200_OK

            response = await client.get("/transactions?user_id=1")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == 1
            assert data[0]["currency"] == "USD"
            assert data[0]["amount"] == "100"
            assert data[0]['status'] == "PROCESSED"
            assert 'created' in data[0]

    @pytest.mark.asyncio
    async def test_post_transaction(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_200_OK

            response = await client.get("/transactions")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["user_id"] == 1
            assert data[0]["currency"] == "USD"
            assert data[0]["amount"] == "100"
            assert data[0]["status"] == "PROCESSED"

            response = await client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert {'currency': 'USD', 'amount': '100'} in data[0]["balances"]

    @pytest.mark.asyncio
    async def test_patch_rollback_transaction(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/1/transactions/1")
            assert request.status_code == status.HTTP_200_OK
            assert request.json() == {'message': 'Transaction rolled back'}

            response = await client.get("/transactions")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data[0]['status'] == "ROLLBACKED"

            response = await client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert {'currency': 'USD', 'amount': '0'} in data[0]["balances"]


class TestNegativeTransAPI:

    @pytest.mark.asyncio
    async def test_trans_when_user_blocked(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/users/1", json={"status": "BLOCKED"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_rolled_back_trans_when_user_blocked(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/users/1", json={"status": "BLOCKED"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/1/transactions/1")
            assert request.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_rolled_back_trans_when_negative_amount(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": 100})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": -50})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/1/transactions/1")
            assert request.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_trans_when_negative_amount(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.post("/1/transactions", json={"currency": "USD", "amount": -50})
            assert request.status_code == status.HTTP_400_BAD_REQUEST
