from pydantic import AnyUrl, BaseSettings, conint


class JwtConfig(BaseSettings):
    algorithm: str
    secret: str
    audience: str
    issuer: str
    expiration: conint(gt=0)

    class Config:
        env_prefix = "JWT_"


class DatabaseConfig(BaseSettings):
    url: AnyUrl
    name: str

    class Config:
        env_prefix = "DATABASE_"


class Config(BaseSettings):
    jwt = JwtConfig()
    database = DatabaseConfig()
