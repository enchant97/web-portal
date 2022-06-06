"""
Misc functions that will assist with other modules
"""

from typing import Any

from quart import current_app

from ..database import models


async def get_system_setting(
        key: str,
        default: Any = None,
        skip_cache: bool = False) -> Any | None:
    """
    gets a system setting stored in db or from cache
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


async def set_system_setting(key: str, value: Any):
    """
    set a system setting stored in db and update cache
    """
    await models.SystemSetting.update_or_create(key=key, defaults=dict(value=value))
    current_app.config[key] = value
