from fastapi import Depends

from app.providers.use_config import use_config
from app.config import Config
from app.email_service import EmailService


async def use_email_service(config: Config = Depends(use_config)):
    return EmailService(config.email)
