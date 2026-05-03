import pytest
from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/api/post", json={"body": body})
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test Post", async_client)


async def test_create_post(async_client: AsyncClient):
    body = "Test Post"

    response = await async_client.post("/api/post", json={"body": body})

    assert response.status_code == 201
    assert {"body": body}.items() <= response.json().items()


async def test_create_post_missing_data(async_client: AsyncClient):

    response = await async_client.post("/api/post", json={})

    assert response.status_code == 422


async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/api/post")

    assert response.status_code == 200
    assert response.json() == [created_post]
