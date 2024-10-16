import logging
from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str
    PLUGINS_PATH: Path
    DATA_PATH: Path
    SECRET_KEY: str | None = None
    SECURE_COOKIES: bool = False
    LOG_LEVEL: str = "INFO"
    SHOW_VERSION_NUMBER: bool = True

    DISABLE_PLUGIN_LOADER: bool = False
    PLUGIN_SKIP_LIST: list[str] | None = None

    UNATTENDED_DEMO_INSTALL: bool = False

    @computed_field
    @property
    def log_level_as_int(self) -> int:
        return logging.getLevelNamesMapping().get(self.LOG_LEVEL.upper(), logging.WARNING)

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    """
    returns the Settings obj
    """
    return Settings()  # type: ignore
