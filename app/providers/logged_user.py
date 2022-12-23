from http import HTTPStatus

from fastapi import Depends, HTTPException
from pymongo.database import Database

from app.providers.access_token import get_access_token
from app.providers.database import get_database
from app.access_token import AccessToken


async def get_logged_user(
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    user = await database.users.find_one({"_id": jwt.sub})

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="The provided token does not match any existing user.",
        )

    return user
