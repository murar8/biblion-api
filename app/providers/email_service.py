from fastapi import Depends

from app.providers.config import get_config
from app.util.config import Config
from app.util.email_service import EmailService


async def get_email_service(config: Config = Depends(get_config)):
    return EmailService(config.email)
