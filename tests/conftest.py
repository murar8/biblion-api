import asyncio
from datetime import datetime
import os

import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app import app
from app.config import Config

# Redefine the event_loop fixture to have a session scope.
# See https://github.com/pytest-dev/pytest-asyncio/issues/68#issuecomment-334083751
@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def app_db():
    config = Config()
    client = AsyncIOMotorClient(config.database.url)
    db = client[config.database.name]

    seed = [
        {
            "_id": "test0",
            "ownerId": os.environ.get("TEST_USER"),
            "content": "console.log('Hello, world!')",
            "name": "test0.js",
            "language": "js",
            "createdAt": datetime(2002, 10, 27, 6, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
        },
        {
            "_id": "test1",
            "ownerId": os.environ.get("TEST_USER"),
            "content": "Hello, world!",
            "name": "test1.txt",
            "language": "txt",
            "createdAt": datetime(2002, 10, 27, 6, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
        },
        {
            "_id": "test2",
            "ownerId": "other@test.com",
            "content": "console.log('Hello, world!')",
            "name": "test2.js",
            "language": "js",
            "createdAt": datetime(2002, 10, 27, 6, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
        },
        {
            "_id": "test3",
            "ownerId": "other@test.com",
            "content": "Hello, world!",
            "name": "test3.txt",
            "language": "txt",
            "createdAt": datetime(2002, 10, 27, 6, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
        },
    ]

    await client.drop_database(config.database.name)
    await db.posts.insert_many(seed)

    yield db


@pytest_asyncio.fixture()
async def app_client():
    client = AsyncClient(
        app=app,
        base_url="https://biblion.com",
        follow_redirects=True,
        headers={"Authorization": f"Bearer {os.environ.get('TEST_TOKEN')}"},
    )

    yield client

    await client.aclose()
