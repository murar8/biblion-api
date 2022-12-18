import os
from datetime import datetime
from http import HTTPStatus

import pytest
import requests
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user(app_client: AsyncClient):
    response = await app_client.get("v1/users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_get_user_non_existent(app_client: AsyncClient):
    response = await app_client.get("v1/users/3e5ef942-6e01-4f35-bc1b-c1278f6c4303")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_get_current_user(app_client: AsyncClient):
    response = await app_client.get("v1/users/me")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_create_user(app_client: AsyncClient):
    body = {"email": "test@gmail.com", "name": "mr_bean", "password": "banana"}
    response = await app_client.post("v1/users", json=body)
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
    response = await app_client.post("v1/users", json=body)

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_create_user_invalid(app_client: AsyncClient):
    body = {"email": "testgmail.com", "name": "mr_bean", "password": "banana"}
    response = await app_client.post("v1/users", json=body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_update_user(app_client: AsyncClient):
    data = {"email": "mrbrown2@user.com"}

    response = await app_client.patch(
        "v1/users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5", json=data
    )

    json = response.json()
    created_at = datetime.fromisoformat(json["createdAt"])
    updated_at = datetime.fromisoformat(json["updatedAt"])

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"
    assert json["email"] == "mrbrown2@user.com"
    assert json["verified"] is False  # Email verification should be invalidated.
    assert json["name"] == "mr_brown"
    assert updated_at > created_at


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_update_user_unset_name(app_client: AsyncClient):
    data = {"name": ""}

    response = await app_client.patch(
        "v1/users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5", json=data
    )

    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert not json["name"]


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_update_user_unauthorized(app_client: AsyncClient):
    response = await app_client.patch(
        "v1/users/34b8028f-a220-498e-85c9-7304e44cb272",
        json={"email": "test@gmail.com"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


# TODO: test user update when user does not exist.


@pytest.mark.asyncio
async def test_login_user(app_client: AsyncClient):
    response = await app_client.get("v1/users/f4c8e142-5a8e-4759-9eec-74d9139dcfd5")
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_with_name(app_client: AsyncClient):
    data = {"name": "mr_brown", "password": "hastasiempre"}
    response = await app_client.post("v1/users/login", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token")
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_with_email(app_client: AsyncClient):
    data = {"email": "mrbrown@user.com", "password": "hastasiempre"}
    response = await app_client.post("v1/users/login", json=data)
    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token")
    assert json["id"] == "f4c8e142-5a8e-4759-9eec-74d9139dcfd5"


@pytest.mark.asyncio
async def test_login_user_bad_credentials(app_client: AsyncClient):
    data = {"name": "mr_brown", "password": "hastasiempres"}
    response = await app_client.post("v1/users/login", json=data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert not response.cookies.get("access_token")


@pytest.mark.asyncio
async def test_login_user_non_existent(app_client: AsyncClient):
    data = {"name": "mr_nope", "password": "hastasiempres"}
    response = await app_client.post("v1/users/login", json=data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not response.cookies.get("access_token")


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_logout_user(app_client: AsyncClient):
    response = await app_client.post("v1/users/logout")
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = await app_client.get("v1/users/me")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_request_verification_code(app_client: AsyncClient):
    response = await app_client.post("v1/users/verify")
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
        "v1/users/verify/03d06d59-5fd5-4c49-bafe-91bab21d1391"
    )

    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert json["verified"] is True


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_verify_user_no_request_found(app_client: AsyncClient):
    response = await app_client.post(
        "v1/users/verify/060ac1bf-4377-4075-b83a-322c0f3f3dfd"
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_request_password_reset(app_client: AsyncClient):
    response = await app_client.post("v1/users/password-reset")
    assert response.status_code == HTTPStatus.NO_CONTENT

    messages = requests.get(
        f"{os.environ['MAILHOG_API_URL']}/api/v2/messages", timeout=1000
    )

    headers = messages.json()["items"][0]["Content"]["Headers"]

    assert headers["From"][0] == "verification@biblion.com"
    assert headers["To"][0] == "mrbrown@user.com"
    assert headers["Subject"][0] == "Password Reset"


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_red"}], indirect=True)
async def test_reset_password(app_client: AsyncClient):
    data = {"password": "hastanoche"}
    response = await app_client.post(
        "v1/users/password-reset/6e94e45a-5f47-4b38-9483-6b1d5d57266b", json=data
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # User should not be able to keep using the same token.

    response = await app_client.get("v1/users/me")
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    # User should be able to login using the new password.

    response = await app_client.post(
        "v1/users/login", json={"name": "mr_red", "password": "hastanoche"}
    )
    assert response.status_code == HTTPStatus.OK

    # Reset code should only be valid for a single operation.

    response = await app_client.post(
        "v1/users/password-reset/6e94e45a-5f47-4b38-9483-6b1d5d57266b", json=data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("app_client", [{"access_token": "mr_brown"}], indirect=True)
async def test_reset_password_no_request_found(app_client: AsyncClient):
    data = {"password": "hastanoche"}
    response = await app_client.post(
        "v1/users/password-reset/fc677ae6-6e43-4b7e-b53c-bb4fe98bff29", json=data
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
