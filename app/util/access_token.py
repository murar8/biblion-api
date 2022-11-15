from __future__ import annotations

import time

import jwt
from pydantic import BaseModel
from typing_extensions import Self

from app.util.config import JwtConfig


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int

    @staticmethod
    def encode(sub: str, config: JwtConfig) -> str:
        iat = time.time()
        exp = iat + config.expiration

        return jwt.encode(
            key=config.secret,
            algorithm=config.algorithm,
            payload={
                "iss": config.issuer,
                "sub": sub,
                "aud": config.audience,
                "iat": iat,
                "exp": exp,
            },
        )

    @staticmethod
    def decode(encoded: str, config: JwtConfig) -> Self:
        payload = jwt.decode(
            jwt=encoded,
            key=config.secret,
            algorithms=config.algorithm,
            audience=config.audience,
            issuer=config.issuer,
        )

        return AccessToken(**payload)
