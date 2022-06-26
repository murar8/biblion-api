from http.client import UNAUTHORIZED
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from providers.config import Settings, get_config

_get_credentials = HTTPBearer()


class JWT(BaseModel):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    azp: str
    gty: str


def get_jwt(
    config: Settings = Depends(get_config),
    auth: HTTPAuthorizationCredentials = Depends(_get_credentials),
):
    try:
        jwks_client = jwt.PyJWKClient(config.jwks_endpoint)
        jwk = jwks_client.get_signing_key_from_jwt(auth.credentials)

        payload = jwt.decode(
            jwt=auth.credentials,
            key=jwk.key,
            algorithms=config.jwt_algorithm,
            audience=config.jwt_audience,
            issuer=config.jwt_issuer,
        )

        return JWT(**payload)
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=UNAUTHORIZED)
