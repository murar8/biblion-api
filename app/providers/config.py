from functools import lru_cache

from app.util.config import Config


@lru_cache()
def get_config():
    return Config()
