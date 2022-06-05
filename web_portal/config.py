from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URI: str
    SECRET_KEY: str
    UNSECURE_LOGIN: Optional[bool] = False
    LOG_LEVEL: Optional[str] = "INFO"

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings():
    """
    returns the Settings obj
    """
    return Settings()
