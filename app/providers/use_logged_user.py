from datetime import timedelta
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

    # We subtract a few seconds from the update time to allow for a bit of
    # clock mismatch if a new token is requested immediately after the update.
    updated_at = (user.passwordUpdatedAt or user.createdAt) - timedelta(seconds=30)

    if updated_at > jwt.iat:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="The provided token has been invalidated.",
        )

    return user
