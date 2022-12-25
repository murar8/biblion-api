from http import HTTPStatus

from fastapi import Depends, HTTPException

from app.access_token import AccessToken
from app.models.documents import UserDocument
from app.providers.use_access_token import use_access_token


async def use_logged_user(jwt: AccessToken = Depends(use_access_token)):
    user = await UserDocument.get(jwt.sub)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="The provided token does not match any existing user.",
        )

    return user
