from fastapi import Depends

from app.providers.config import get_config
from app.config import Config
from app.email_service import EmailService


async def get_email_service(config: Config = Depends(get_config)):
    return EmailService(config.email)
