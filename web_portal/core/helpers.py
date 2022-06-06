"""
Misc functions that will assist with other modules
"""

from typing import Any

from quart import current_app

from ..database import models


async def get_system_setting(
        key: str,
        /,
        *,
        default: Any = None,
        skip_cache: bool = False) -> Any | None:
    """
    Gets a system setting stored in db or from cache

        :param key: The setting's key
        :param default: The default value to use if no setting was found, defaults to None
        :param skip_cache: Whether the skip cache and load from db directly, defaults to False
        :return: The loaded value or None
    """
    value = None

    if not skip_cache:
        value = current_app.config.get(key)

    if value is None:
        setting_row = await models.SystemSetting.get_or_none(key=key)
        if setting_row is not None:
            value = setting_row.value
            # update cache for next time
            current_app.config[key] = value

    return value if value is not None else default


async def set_system_setting(key: str, value: Any, /):
    """
    Set a system setting stored in db and updates cache

        :param key: The setting's key
        :param value: Value to update setting to
    """
    await models.SystemSetting.update_or_create(key=key, defaults=dict(value=value))
    current_app.config[key] = value


async def remove_system_setting(key: str, /):
    """
    Removes a set system setting stored in db and cache

        :param key: The setting's key
    """
    await models.SystemSetting.filter(key=key).delete()
    current_app.config.pop(key, None)