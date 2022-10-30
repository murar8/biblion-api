from __future__ import annotations

from typing import Optional
from typing_extensions import Self

import jwt
from pydantic import BaseModel

from app.util.config import JwtConfig


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    azp: str
    gty: str

    @staticmethod
    def try_from_str(encoded: str, config: JwtConfig) -> Optional[Self]:
        try:
            payload = jwt.decode(
                jwt=encoded,
                key=config.key,
                algorithms=config.algorithm,
                audience=config.audience,
                issuer=config.issuer,
            )

            return AccessToken(**payload)
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return None
