# from .conftest import client
import pytest
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register(ac):
    response = await ac.post("/auth/register", json={
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == "user@example.com"
    assert data['is_active'] is True
    assert data['is_superuser'] is False
    assert data['is_verified'] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register_existed(ac):
    response = await ac.post("/auth/register", json={
        "email": "user@example.com",
        "password": "string2",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == "REGISTER_USER_ALREADY_EXISTS"


created_user_token = None


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login(ac):
    response = await ac.post("/auth/jwt/login", data={
        "username": "user@example.com",
        "password": "string",
        "grant_type": "password",
    })
    assert response.status_code == 200
    data = response.json()
    global created_user_token
    created_user_token = data['access_token']


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login_wrong_creds(ac):
    response = await ac.post("/auth/jwt/login", data={
        "username": "user@example.com",
        "password": "password",
        "grant_type": "password",
    })

    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_logout(ac_logined):
    response = await ac_logined.post("/auth/jwt/logout", headers={
        "Authorization": f"Bearer {created_user_token}"
    })

    assert response.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_logout_no_token(ac_logined):
    response = await ac_logined.post("/auth/jwt/logout")

    assert response.status_code == 401
    data = response.json()
    assert data['detail'] == "Unauthorized"
