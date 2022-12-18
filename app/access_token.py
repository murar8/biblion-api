from __future__ import annotations

import time
import uuid
from datetime import datetime

import jwt
from pydantic import BaseModel
from typing_extensions import Self

from app.config import JwtConfig


class AccessToken(BaseModel):
    iss: str
    sub: uuid.UUID
    aud: str
    iat: datetime
    exp: datetime

    @staticmethod
    def encode(sub: uuid.UUID, config: JwtConfig) -> str:
        iat = time.time() - 1  # Make sure the token is immediately valid.
        exp = iat + config.expiration

        return jwt.encode(
            key=config.secret,
            algorithm=config.algorithm,
            payload={
                "iss": config.issuer,
                "sub": str(sub),
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
