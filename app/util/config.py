from pydantic import AnyUrl, conint
import pydantic


class JwtConfig(pydantic.BaseSettings):
    algorithm: str
    secret: str
    audience: str
    issuer: str
    expiration: conint(gt=0)

    class Config:
        env_prefix = "JWT_"


class DatabaseConfig(pydantic.BaseSettings):
    url: AnyUrl
    name: str

    class Config:
        env_prefix = "DATABASE_"


class Config(pydantic.BaseSettings):
    jwt = JwtConfig()
    database = DatabaseConfig()
