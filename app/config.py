from typing import Optional

from pydantic import BaseSettings, SecretStr, validator


class JwtConfig(BaseSettings):
    audience: str
    algorithm: str
    issuer: str
    jwks_endpoint: Optional[str]
    key: Optional[str]

    @validator("key")
    def check_key(cls, key, values):
        if not values.get("jwks_endpoint") and not key:
            raise ValueError("No valid JWKS endpoint or key supplied.")
        return key

    class Config:
        env_prefix = "JWT_"


class DatabaseConfig(BaseSettings):
    url: str
    name: str

    class Config:
        env_prefix = "DATABASE_"


class Config(BaseSettings):
    jwt = JwtConfig()
    database = DatabaseConfig()
    secret_key: SecretStr
