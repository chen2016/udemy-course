import pytest
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
