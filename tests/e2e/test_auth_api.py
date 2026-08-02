import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_patient(async_client: AsyncClient):
    # Register
    reg_payload = {
        "email": "newpatient@test.com",
        "password": "SecurePassword123!",
        "full_name": "Jane Patient",
        "role": "PATIENT",
        "phone_number": "+15554443333",
    }
    resp = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "PATIENT"

    # Login
    login_payload = {
        "email": "newpatient@test.com",
        "password": "SecurePassword123!",
    }
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    assert "access_token" in login_data["data"]


@pytest.mark.asyncio
async def test_login_invalid_password(async_client: AsyncClient):
    login_payload = {
        "email": "nonexistent@test.com",
        "password": "WrongPassword!",
    }
    resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"
