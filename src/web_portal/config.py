from functools import lru_cache
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_URL: str
    ADMIN_CREATE_OVERRIDE: Optional[bool] = False
    SECRET_KEY: str
    UNSECURE_LOGIN: Optional[bool] = False
    PORTAL_SECURED: Optional[bool] = False
    SHOW_PANEL_HEADERS: Optional[bool] = True

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
