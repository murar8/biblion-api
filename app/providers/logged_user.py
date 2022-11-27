import uuid
from http import HTTPStatus

from fastapi import Depends, HTTPException
from pymongo.database import Database

from app.providers.auth import get_jwt
from app.providers.database import get_db
from app.util.access_token import AccessToken


async def get_logged_user(
    jwt: AccessToken = Depends(get_jwt),
    database: Database = Depends(get_db),
):
    uid = uuid.UUID(jwt.sub)
    user = await database.users.find_one({"_id": uid})

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No user found for the provided credentials.",
        )

    return user
