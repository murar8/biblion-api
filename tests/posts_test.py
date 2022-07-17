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


@pytest.mark.asyncio
async def test_get_posts(app_client: AsyncClient):
    response = await app_client.get("posts")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 4
    assert json["token"]


@pytest.mark.asyncio
async def test_get_posts_paging(app_client: AsyncClient):
    params = {"count": 2, "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "test0"
    assert json["data"][1]["id"] == "test1"

    params = {"count": 4, "sort": "id:asc", "token": json["token"]}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "test2"
    assert json["data"][1]["id"] == "test3"


@pytest.mark.asyncio
async def test_get_posts_sort(app_client: AsyncClient):
    response = await app_client.get("posts", params={"sort": "createdAt:desc"})
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["data"][0]["id"] == "test1"
    assert json["data"][-1]["id"] == "test3"


@pytest.mark.asyncio
async def test_get_posts_updated_at(app_client: AsyncClient):
    params = {
        "updatedAt": f"gt:{datetime(2002, 10, 28, 14, 0, 0).isoformat()}",
        "sort": "id:asc",
    }
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "test2"
    assert json["data"][1]["id"] == "test3"


@pytest.mark.asyncio
async def test_get_posts_updated_at(app_client: AsyncClient):
    params = {
        "createdAt": f"gt:{datetime(2002, 10, 27, 3, 0, 0).isoformat()}",
        "sort": "id:asc",
    }
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 1
    assert json["data"][0]["id"] == "test1"


@pytest.mark.asyncio
async def test_get_posts_owner_id(app_client: AsyncClient):
    params = {"ownerId": os.environ.get("TEST_USER"), "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "test0"
    assert json["data"][1]["id"] == "test1"


@pytest.mark.asyncio
async def test_get_posts_language(app_client: AsyncClient):
    params = {"language": "js", "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "test0"
    assert json["data"][1]["id"] == "test2"
