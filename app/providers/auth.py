from http import HTTPStatus

from fastapi import Cookie, Depends, HTTPException
from jwt import DecodeError, ExpiredSignatureError

from app.providers.config import Config, get_config
from app.util.access_token import AccessToken


def get_jwt(
    config: Config = Depends(get_config),
    access_token: str = Cookie(),
):
    try:
        return AccessToken.decode(access_token, config.jwt)
    except (DecodeError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid JWT.")
    except (ExpiredSignatureError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Expired JWT.")
