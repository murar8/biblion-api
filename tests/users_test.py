import os
from datetime import datetime
from http import HTTPStatus

import pytest
import requests
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user(app_client: AsyncClient):
    response = await app_client.get("users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_get_user_non_existent(app_client: AsyncClient):
    response = await app_client.get("users/3e5ef942-6e01-4f35-bc1b-c1278f6c4303")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_create_user(app_client: AsyncClient):
    body = {"email": "test@gmail.com", "name": "mr_bean", "password": "banana"}
    response = await app_client.post("users", json=body)
    json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert len(json["id"]) > 0
    assert json["email"] == "test@gmail.com"
    assert json["name"] == "mr_bean"
    assert json["verified"] is False
    assert datetime.fromisoformat(json["createdAt"])
    assert datetime.fromisoformat(json["updatedAt"])


@pytest.mark.asyncio
async def test_create_user_already_exists(app_client: AsyncClient):
    body = {"email": "mrgreen@user.com", "name": "mr_bean", "password": "banana"}
    response = await app_client.post("users", json=body)

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_create_user_invalid(app_client: AsyncClient):
    body = {"email": "testgmail.com", "name": "mr_bean", "password": "banana"}
    response = await app_client.post("users", json=body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_update_user(app_client: AsyncClient):
    response = await app_client.patch(
        "users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5",
        json={"email": "test@gmail.com"},
    )

    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["email"] == "test@gmail.com"
    assert json["name"] == "mr_brown"
    created_at = datetime.fromisoformat(json["createdAt"])
    updated_at = datetime.fromisoformat(json["updatedAt"])
    assert updated_at > created_at


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_update_user_unauthorized(app_client: AsyncClient):
    response = await app_client.patch(
        "users/34b8028f-a220-498e-85c9-7304e44cb272",
        json={"email": "test@gmail.com"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


# TODO: test user update when user does not exist.


@pytest.mark.asyncio
async def test_login_user(app_client: AsyncClient):
    response = await app_client.get("users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_with_name(app_client: AsyncClient):
    data = {"name": "mr_brown", "password": "hastasiempre"}
    response = await app_client.post("users/login", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token")
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_with_email(app_client: AsyncClient):
    data = {"email": "mrbrown@user.com", "password": "hastasiempre"}
    response = await app_client.post("users/login", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token")
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_bad_credentials(app_client: AsyncClient):
    data = {"name": "mr_brown", "password": "hastasiempres"}
    response = await app_client.post("users/login", json=data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert not response.cookies.get("access_token")


@pytest.mark.asyncio
async def test_login_user_non_existent(app_client: AsyncClient):
    data = {"name": "mr_nope", "password": "hastasiempres"}
    response = await app_client.post("users/login", json=data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not response.cookies.get("access_token")


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_request_verification_code(app_client: AsyncClient):
    response = await app_client.post("users/verification-code")
    assert response.status_code == HTTPStatus.NO_CONTENT

    messages = requests.get(
        f"{os.environ['MAILHOG_API_URL']}/api/v2/messages", timeout=1000
    )

    headers = messages.json()["items"][0]["Content"]["Headers"]

    assert headers["From"][0] == "verification@biblion.com"
    assert headers["To"][0] == "mrbrown@user.com"
    assert headers["Subject"][0] == "Verify your address"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_red"}], indirect=True)
async def test_verify_user(app_client: AsyncClient):
    response = await app_client.post(
        "users/verify/03d06d59-5fd5-4c49-bafe-91bab21d1391"
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_verify_user_no_request_found(app_client: AsyncClient):
    response = await app_client.post(
        "users/verify/060ac1bf-4377-4075-b83a-322c0f3f3dfd"
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
