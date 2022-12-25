from http import HTTPStatus

from fastapi import Depends, HTTPException

from app.access_token import AccessToken
from app.models.database import User
from app.providers.access_token import get_access_token


async def get_logged_user(jwt: AccessToken = Depends(get_access_token)):
    user = await User.get(jwt.sub)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="The provided token does not match any existing user.",
        )

    return user
