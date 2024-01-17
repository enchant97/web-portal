from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str
    PLUGINS_PATH: Path
    DATA_PATH: Path
    SECRET_KEY: str | None = None
    SECURE_COOKIES: bool | None = False
    LOG_LEVEL: str | None = "INFO"
    SHOW_VERSION_NUMBER: bool | None = True

    DISABLE_PLUGIN_LOADER: bool = False
    PLUGIN_SKIP_LIST: list[str] | None = None

    UNATTENDED_DEMO_INSTALL: bool | None = False

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    """
    returns the Settings obj
    """
    return Settings()
