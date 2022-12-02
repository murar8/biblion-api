import pydantic
from pydantic import AnyUrl, EmailStr, conint


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


class EmailConfig(pydantic.BaseSettings):
    sender: EmailStr
    smtp_server: str
    verification_expiration: conint(gt=0)
    password_reset_expiration: conint(gt=0)

    class Config:
        env_prefix = "EMAIL_"


class WebsiteConfig(pydantic.BaseSettings):
    base_url: AnyUrl

    class Config:
        env_prefix = "WEBSITE_"


class Config(pydantic.BaseSettings):
    website = WebsiteConfig()
    jwt = JwtConfig()
    database = DatabaseConfig()
    email = EmailConfig()
