from pydantic import BaseSettings


class JwtConfig(BaseSettings):
    audience: str
    algorithm: str
    issuer: str
    key: str

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
