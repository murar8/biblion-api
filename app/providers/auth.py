from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..access_token import AccessToken
from ..providers.config import Config, get_config

_get_credentials = HTTPBearer()


def get_jwt(
    config: Config = Depends(get_config),
    auth: HTTPAuthorizationCredentials = Depends(_get_credentials),
):
    if token := AccessToken.try_from_str(auth.credentials, config.jwt):
        return token
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid JWT.")
