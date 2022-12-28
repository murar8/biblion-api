import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app import app
from tests.init_db import init_db
from tests.test_access_tokens import test_access_tokens


@pytest_asyncio.fixture()
async def app_client(request):
    client_config = {
        "app": app,
        "base_url": "https://biblion.io",
        "follow_redirects": True,
    }

    if hasattr(request, "param") and "logged_user" in request.param:
        access_token = test_access_tokens[request.param["logged_user"]]
        client_config["cookies"] = [("access_token", access_token)]

    # Using LifespanManager to run the startup and shutdown events.
    # See https://github.com/tiangolo/fastapi/issues/2003#issuecomment-801140731

    async with AsyncClient(**client_config) as client, LifespanManager(app):
        await init_db()
        yield client
