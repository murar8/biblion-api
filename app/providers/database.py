from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
from pymongo.database import Database

from app.providers.config import Config, get_config


async def get_database(config: Config = Depends(get_config)) -> Database:
    client = AsyncIOMotorClient(config.database.url, uuidRepresentation="standard")
    database: Database = client[config.database.name]

    await database.users.create_indexes(
        [IndexModel("name", unique=True), IndexModel("email", unique=True)]
    )

    return database
