from http import HTTPStatus

from fastapi import Cookie, Depends, HTTPException
from jwt import DecodeError, ExpiredSignatureError

from app.providers.use_config import Config, use_config
from app.access_token import AccessToken


def use_access_token(
    config: Config = Depends(use_config),
    access_token: str | None = Cookie(default=None),
):
    """
    NOTE: This function will return a valid access token even when the token has been
    invalidated after a password update, prefer using `use_logged_user` instead.
    """

    if access_token is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="No JWT found.")

    try:
        return AccessToken.decode(access_token, config.jwt)
    except DecodeError as exception:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid JWT."
        ) from exception
    except ExpiredSignatureError as exception:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Expired JWT."
        ) from exception
