from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URI: str
    PLUGINS_PATH: Path
    DATA_PATH: Path
    SECRET_KEY: Optional[str] = None
    SECURE_COOKIES: Optional[bool] = False
    LOG_LEVEL: Optional[str] = "INFO"
    SHOW_VERSION_NUMBER: Optional[bool] = True

    DISABLE_PLUGIN_LOADER: bool = False
    PLUGIN_SKIP_LIST: Optional[list[str]] = None

    UNATTENDED_DEMO_INSTALL: Optional[bool] = False

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
