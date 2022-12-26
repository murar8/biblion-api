from datetime import datetime
from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_post(app_client: AsyncClient):
    response = await app_client.get("v1/posts/bdu764rt")

    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "bdu764rt"
    assert json["creatorId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Hello, world!"
    assert json["name"] == "hello.txt"
    assert json["language"] is None
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
async def test_get_post_non_existent(app_client: AsyncClient):
    response = await app_client.get("v1/posts/fakeid")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_posts(app_client: AsyncClient):
    response = await app_client.get("v1/posts", params={"limit": "32"})
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["hasMore"] is False
    assert json["totalCount"] == 4
    assert json["data"][0]["id"] == "ctrdg53d"
    assert json["data"][-1]["id"] == "bdu764rt"


@pytest.mark.asyncio
async def test_get_posts_paging(app_client: AsyncClient):
    query = {"limit": "2", "skip": "1"}
    response = await app_client.get("v1/posts", params=query)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["totalCount"] == 4
    assert json["hasMore"] is True
    assert json["data"][0]["id"] == "d7yhmbr5"
    assert json["data"][1]["id"] == "a46yh2d3"


@pytest.mark.asyncio
async def test_get_posts_owner_id(app_client: AsyncClient):
    query = {"creatorId": "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"}
    response = await app_client.get("v1/posts", params=query)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["totalCount"] == 2
    assert json["data"][0]["id"] == "a46yh2d3"
    assert json["data"][1]["id"] == "bdu764rt"


@pytest.mark.asyncio
async def test_get_posts_language(app_client: AsyncClient):
    query = {"language": "tsx"}
    response = await app_client.get("v1/posts", params=query)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["totalCount"] == 1
    assert json["data"][0]["id"] == "ctrdg53d"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_create_post(app_client: AsyncClient):
    response = await app_client.post("v1/posts", json={"content": "Test"})
    json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert len(json["id"]) > 0
    assert json["creatorId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Test"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_red"}], indirect=True)
async def test_create_post_unverified(app_client: AsyncClient):
    response = await app_client.post("v1/posts", json={"content": "Test"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_update_post(app_client: AsyncClient):
    now = datetime.utcnow()
    body = {"content": "Hello, You!"}
    response = await app_client.put("v1/posts/bdu764rt", json=body)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "bdu764rt"
    assert json["creatorId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Hello, You!"
    assert json["name"] is None
    assert json["language"] is None
    assert datetime.fromisoformat(json["updatedAt"]) >= now


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_update_post_non_existent(app_client: AsyncClient):
    body = {"content": "console.log('Update!')"}
    response = await app_client.put("v1/posts/fakeid", json=body)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_update_post_non_owned(app_client: AsyncClient):
    body = {"content": "console.log('Update!')"}
    response = await app_client.put("v1/posts/ctrdg53d", json=body)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_delete_post(app_client: AsyncClient):
    response = await app_client.delete("v1/posts/bdu764rt")
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_delete_post_non_owned(app_client: AsyncClient):
    response = await app_client.delete("v1/posts/ctrdg53d")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"logged_user": "mr_brown"}], indirect=True)
async def test_delete_post_non_existent(app_client: AsyncClient):
    response = await app_client.delete("v1/posts/fakeid")
    assert response.status_code == HTTPStatus.NOT_FOUND
