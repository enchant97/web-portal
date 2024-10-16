"""
Misc functions that will assist with other modules
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from quart import Response, current_app, redirect, request, url_for

from ..database import models


async def get_system_setting(
    key: str, /, *, default: Any = None, skip_cache: bool = False
) -> Any | None:
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
    await models.SystemSetting.update_or_create(key=key, defaults={"value": value})
    current_app.config[key] = value


async def remove_system_setting(key: str, /):
    """
    Removes a set system setting stored in db and cache

        :param key: The setting's key
    """
    await models.SystemSetting.filter(key=key).delete()
    current_app.config.pop(key, None)


def redirect_using_back_to(func: Callable) -> Callable:
    """
    Used to decorate a Quart response,
    allowing redirects to a provided back_to request arg
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Response:
        response = await func(*args, **kwargs)
        if response is not None:
            # allow the function to overide wrapper
            return response
        # redirect from request args
        if (back_to_url := request.args.get("back_to")) is not None:
            return redirect(back_to_url)
        # failover if nothing else applies
        return redirect(url_for("portal.portal"))

    return wrapper
