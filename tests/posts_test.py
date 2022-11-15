from datetime import datetime
from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_post(app_client: AsyncClient):
    response = await app_client.get("posts/bdu764rt")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "bdu764rt"
    assert json["ownerId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Hello, world!"
    assert json["name"] == "hello.txt"
    assert json["language"] == "txt"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_post_non_existent(app_client: AsyncClient):
    response = await app_client.get("posts/fakeid")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts(app_client: AsyncClient):
    response = await app_client.get("posts")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 4
    assert json["token"]


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts_paging(app_client: AsyncClient):
    params = {"count": 2, "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "a46yh2d3"
    assert json["data"][1]["id"] == "bdu764rt"

    params = {"count": 4, "sort": "id:asc", "token": json["token"]}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "ctrdg53d"
    assert json["data"][1]["id"] == "d7yhmbr5"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts_sort(app_client: AsyncClient):
    response = await app_client.get("posts", params={"sort": "createdAt:desc"})
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["data"][0]["id"] == "bdu764rt"
    assert json["data"][-1]["id"] == "d7yhmbr5"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts_updated_at(app_client: AsyncClient):
    params = {
        "updatedAt": f"gt:{datetime(2002, 10, 28, 14, 0, 0).isoformat()}",
        "sort": "id:asc",
    }
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "ctrdg53d"
    assert json["data"][1]["id"] == "d7yhmbr5"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts_owner_id(app_client: AsyncClient):
    params = {"ownerId": "34b8028f-a220-498e-85c9-7304e44cb272", "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 2
    assert json["data"][0]["id"] == "ctrdg53d"
    assert json["data"][1]["id"] == "d7yhmbr5"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": False}], indirect=True)
async def test_get_posts_language(app_client: AsyncClient):
    params = {"language": "js", "sort": "id:asc"}
    response = await app_client.get("posts", params=params)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json["data"]) == 1
    assert json["data"][0]["id"] == "a46yh2d3"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_create_post(app_client: AsyncClient):
    response = await app_client.post("posts", json={"content": "Test"})
    json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert len(json["id"]) > 0
    assert json["ownerId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Test"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_update_post(app_client: AsyncClient):
    now = datetime.utcnow()
    data = {"content": "Hello, You!"}
    response = await app_client.patch("posts/bdu764rt", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "bdu764rt"
    assert json["ownerId"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["content"] == "Hello, You!"
    assert json["name"] == "hello.txt"
    assert json["language"] == "txt"
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"]) >= now


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_update_post_non_existent(app_client: AsyncClient):
    data = {"content": "console.log('Update!')"}
    response = await app_client.patch("posts/fakeid", json=data)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_update_post_non_owned(app_client: AsyncClient):
    data = {"content": "console.log('Update!')"}
    response = await app_client.patch("posts/ctrdg53d", json=data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_delete_post(app_client: AsyncClient):
    response = await app_client.delete("posts/bdu764rt")
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_delete_post_non_owned(app_client: AsyncClient):
    response = await app_client.delete("posts/ctrdg53d")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"authorized": True}], indirect=True)
async def test_delete_post_non_existent(app_client: AsyncClient):
    response = await app_client.delete("posts/fakeid")
    assert response.status_code == HTTPStatus.NOT_FOUND
