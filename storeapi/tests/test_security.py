from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from storeapi import security
from storeapi.conifg import config


def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com")
    assert user is None


def test_create_access_token(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[security.ALGORITHM])
    assert payload["sub"] == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(Exception):
        await security.authenticate_user("nonexistent@example.com", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(Exception):
        await security.authenticate_user(registered_user["email"], "wrongpassword")


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc:
        await security.get_current_user("invalid.token.here")
    assert exc.value.status_code == 401


@pytest.mark.anyio
async def test_get_current_user_expired_token(registered_user: dict):
    expired_token = security.create_access_token(
        registered_user["email"], expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(HTTPException) as exc:
        await security.get_current_user(expired_token)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail


@pytest.mark.anyio
async def test_get_current_user_not_in_db():
    token = security.create_access_token("ghost@example.com")
    with pytest.raises(HTTPException) as exc:
        await security.get_current_user(token)
    assert exc.value.status_code == 401
