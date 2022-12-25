from functools import lru_cache

from app.config import Config


@lru_cache()
def use_config():
    return Config()
