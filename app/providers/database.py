from fastapi import Depends
from motor.core import Database
from motor.motor_asyncio import AsyncIOMotorClient

from app.providers.config import Config, get_config


async def get_db(config: Config = Depends(get_config)) -> Database:
    client = AsyncIOMotorClient(config.database.url, uuidRepresentation="standard")
    db = client[config.database.name]
    return db
