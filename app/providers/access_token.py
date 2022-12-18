from http import HTTPStatus

from fastapi import Cookie, Depends, HTTPException
from jwt import DecodeError, ExpiredSignatureError

from app.providers.config import Config, get_config
from app.access_token import AccessToken


def get_access_token(
    config: Config = Depends(get_config),
    access_token: str | None = Cookie(default=None),
):
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
