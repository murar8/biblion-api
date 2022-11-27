import asyncio
import uuid
from datetime import datetime

import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app import app
from app.util.config import Config


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
    client = AsyncIOMotorClient(config.database.url, uuidRepresentation="standard")
    database = client[config.database.name]

    posts_seed = [
        {
            "_id": "a46yh2d3",
            "ownerId": uuid.UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
            "content": "console.log('Hello, world!')",
            "name": "hello.js",
            "language": "js",
            "createdAt": datetime(2002, 10, 27, 2, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
        },
        {
            "_id": "bdu764rt",
            "ownerId": uuid.UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
            "content": "Hello, world!",
            "name": "hello.txt",
            "language": "txt",
            "createdAt": datetime(2002, 10, 27, 6, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 11, 0, 0),
        },
        {
            "_id": "ctrdg53d",
            "ownerId": uuid.UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
            "content": "console.log('Hello, world!')",
            "name": "test.ts",
            "language": "ts",
            "createdAt": datetime(2002, 10, 27, 3, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 22, 0, 0),
        },
        {
            "_id": "d7yhmbr5",
            "ownerId": uuid.UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
            "content": "Hello, world!",
            "name": "hi.txt",
            "language": "txt",
            "createdAt": datetime(2002, 10, 27, 1, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
        },
    ]

    users_seed = [
        {
            "_id": uuid.UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
            "email": "mrbrown@user.com",
            "name": "mr_brown",
            "password_hash": (
                # pw: "hastasiempre"
                b"$2b$12$AccWeQEg2szEkty9YCWLa.1Y2snNhc.DTmk97Qveg8hpDgm9.O2kG"
            ),
            "verified": True,
            "createdAt": datetime(2002, 10, 27, 2, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
        },
        {
            "_id": uuid.UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
            "email": "mrgreen@user.com",
            "name": "mr_green",
            "password_hash": (
                # pw: "hastanunca"
                b"$2b$12$tToXPOgFqXrqjuIdCXODZeXK0IfL.kz7sZ1/SxWRvN3Zn.TZYe7MW"
            ),
            "verified": False,
            "createdAt": datetime(2002, 10, 27, 2, 0, 0),
            "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
        },
        {
            "_id": uuid.UUID("af71f215-c3f8-441f-9498-e75f8dfbcf4b"),
            "email": "mrred@user.com",
            "name": "mr_red",
            "password_hash": (
                # pw: "hastanunca"
                b"$2b$12$tToXPOgFqXrqjuIdCXODZeXK0IfL.kz7sZ1/SxWRvN3Zn.TZYe7MW"
            ),
            "verified": False,
            "createdAt": datetime(2002, 10, 22, 2, 0, 0),
            "updatedAt": datetime(2002, 11, 28, 14, 0, 0),
            "verification_code": uuid.UUID("03d06d59-5fd5-4c49-bafe-91bab21d1391"),
            "verification_code_iat": datetime.now(),
        },
    ]

    await client.drop_database(config.database.name)
    await database.posts.insert_many(posts_seed)
    await database.users.insert_many(users_seed)

    yield database


@pytest_asyncio.fixture()
async def app_client(request):
    client = AsyncClient(
        app=app,
        base_url="https://biblion.com",
        follow_redirects=True,
    )

    if hasattr(request, "param") and "access_token" in request.param:
        match request.param["access_token"]:
            case "mr_brown":
                client.cookies.set(
                    "access_token",
                    #   iss: https://api.biblion.com
                    #   sub: f4c8e142-5a8e-4759-9eec-74d9139dcfd5
                    #   aud: https://api.biblion.com
                    #   iat: 1667766384.0424864
                    #   exp: 2667766384.042486
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FwaS5ia"
                    "WJsaW9uLmNvbSIsInN1YiI6ImY0YzhlMTQyLTVhOGUtNDc1OS05ZWVjLTc0ZDkxMzl"
                    "kY2ZkNSIsImF1ZCI6Imh0dHBzOi8vYXBpLmJpYmxpb24uY29tIiwiaWF0IjoxNjY3N"
                    "zY2Mzg0LjA0MjQ4NjQsImV4cCI6MjY2Nzc2NjM4NC4wNDI0ODZ9.Dnk6k40e56or2u"
                    "79rPJelZnYwJHY5QoLwN94kkFMcP0",
                )

            case "mr_red":
                client.cookies.set(
                    "access_token",
                    #   iss: https://api.biblion.com
                    #   sub: af71f215-c3f8-441f-9498-e75f8dfbcf4b
                    #   aud: https://api.biblion.com
                    #   iat: 1667766384.0424864
                    #   exp: 2667766384.042486
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FwaS5ia"
                    "WJsaW9uLmNvbSIsInN1YiI6ImFmNzFmMjE1LWMzZjgtNDQxZi05NDk4LWU3NWY4ZGZ"
                    "iY2Y0YiIsImF1ZCI6Imh0dHBzOi8vYXBpLmJpYmxpb24uY29tIiwiaWF0IjoxNjY3N"
                    "zY2Mzg0LjA0MjQ4NjQsImV4cCI6MjY2Nzc2NjM4NC4wNDI0ODZ9.4LRHOR2oQ9G_Dl"
                    "p7q5uSMci195sdY8KflWcU4uE2e2g",
                )

            case _:
                raise Exception(f"Invalid token: {request.param['access_token']}")

    yield client

    await client.aclose()
