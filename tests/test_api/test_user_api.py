import pytest
from httpx import ASGITransport, AsyncClient

from fastapi import FastAPI, status


class TestUserAPI:

    @pytest.mark.asyncio
    async def test_get_user(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            response = await client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_user_by_query(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            user_id = 2
            email = "test2@email.com"
            stat = "ACTIVE"
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK
            request = await client.post("/users", json={"email": email})
            assert request.status_code == status.HTTP_200_OK

            response = await client.get(f"/users?user_id={user_id}")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()[0]["email"] == email

            response = await client.get(f"/users?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()[0]["email"] == email

            response = await client.get(f"/users?user_status={stat}")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_register_user(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            response = await client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["email"] == "test@email.com"
            assert data[0]["status"] == "ACTIVE"
            assert len(data[0]["balances"]) == 10
            assert all(map(lambda wallet: wallet["amount"] == "0", data[0]["balances"]))

    @pytest.mark.asyncio
    async def test_update_user(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK

            request = await client.patch("/users/1", json={"status": "BLOCKED"})
            assert request.status_code == status.HTTP_200_OK

            response = await client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()[0]["status"] == "BLOCKED"


class TestNegativeUserAPI:

    @pytest.mark.asyncio
    async def test_reg_two_users_with_one_email(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:
            request = await client.post("/users", json={"email": "test@email.com"})
            assert request.status_code == status.HTTP_200_OK
            request = await client.post("/users", json={"email": "test@e,ail.com"})
            assert request.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_email_with_no_valid_email(self, overridden_app: FastAPI) -> None:
        async with AsyncClient(transport=ASGITransport(app=overridden_app), base_url="http://test") as client:

            request = await client.post("/users", json={"email": "test@email"})
            assert request.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            request = await client.post("/users", json={"email": "@email.com"})
            assert request.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            request = await client.post("/users", json={"email": "test@.com"})
            assert request.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            request = await client.post("/users", json={"email": "test"})
            assert request.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
