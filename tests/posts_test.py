from datetime import datetime
from http import HTTPStatus
import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_post(app_client: AsyncClient):
    response = await app_client.get("posts/test0")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "test0"
    assert json["ownerId"] == os.environ.get("TEST_USER")
    assert json["content"] == "console.log('Hello, world!')"
    assert json["name"] == "test0.js"
    assert json["language"] == "js"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
async def test_get_post_non_existent(app_client: AsyncClient):
    response = await app_client.get("posts/fakeid")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_create_post(app_client: AsyncClient):
    response = await app_client.post("posts", json={"content": "Test"})
    json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert len(json["id"]) > 0
    assert json["ownerId"] == os.environ.get("TEST_USER")
    assert json["content"] == "Test"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
async def test_update_post(app_client: AsyncClient):
    now = datetime.utcnow()
    data = {"content": "console.log('Update!')"}
    response = await app_client.patch("posts/test0", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "test0"
    assert json["ownerId"] == os.environ.get("TEST_USER")
    assert json["content"] == data["content"]
    assert json["name"] == "test0.js"
    assert json["language"] == "js"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"]) >= now


@pytest.mark.asyncio
async def test_update_post_non_existent(app_client: AsyncClient):
    data = {"content": "console.log('Update!')"}
    response = await app_client.patch("posts/fakeid", json=data)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_post_non_owned(app_client: AsyncClient):
    data = {"content": "console.log('Update!')"}
    response = await app_client.patch("posts/test2", json=data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
