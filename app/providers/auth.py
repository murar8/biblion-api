from http import HTTPStatus

from app.util.access_token import AccessToken
from app.providers.config import Config, get_config
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_get_credentials = HTTPBearer()


def get_jwt(
    config: Config = Depends(get_config),
    auth: HTTPAuthorizationCredentials = Depends(_get_credentials),
):
    if token := AccessToken.try_from_str(auth.credentials, config.jwt):
        return token
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid JWT.")
