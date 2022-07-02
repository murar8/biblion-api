from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
import jwt

from .config import JwtConfig


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    azp: str
    gty: str

    @staticmethod
    def try_from_str(encoded: str, config: JwtConfig) -> Optional[AccessToken]:
        try:
            if config.jwks_endpoint:
                jwks_client = jwt.PyJWKClient(config.jwks_endpoint)
                jwk = jwks_client.get_signing_key_from_jwt(encoded)
                key = jwk.key
            else:
                key = config.key

            payload = jwt.decode(
                jwt=encoded,
                key=key,
                algorithms=config.algorithm,
                audience=config.audience,
                issuer=config.issuer,
            )

            return AccessToken(**payload)
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return None
