from functools import lru_cache

from app.config import Config


@lru_cache()
def get_config():
    return Config()
