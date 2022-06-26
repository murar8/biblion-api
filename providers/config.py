from functools import lru_cache
from urllib.parse import urljoin
from pydantic import BaseSettings, SecretStr, constr


class Settings(BaseSettings):
    secret_key: SecretStr

    database_url: str

    jwt_audience: str
    jwt_algorithm: str
    jwt_issuer: str

    @property
    def jwks_endpoint(self):
        return urljoin(self.jwt_issuer, ".well-known/jwks.json")

    class Config:
        env_file = ".env"


@lru_cache()
def get_config():
    return Settings()
