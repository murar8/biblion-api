from fastapi import Depends
from motor.core import Database
from motor.motor_asyncio import AsyncIOMotorClient

from ..providers.config import Config, get_config


async def get_db(config: Config = Depends(get_config)) -> Database:
    client = AsyncIOMotorClient(config.database.url)
    db = client[config.database.name]
    return db
