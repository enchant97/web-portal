"""
Module to assist with authentication
"""

from functools import wraps
from typing import Any, Callable

import quart_auth
from quart import abort

from ..database import models
from .constants import SystemSettingKeys
from .helpers import get_system_setting


class AuthUserEnhanced(quart_auth.AuthUser):
    @property
    async def is_authenticated_admin(self):
        if await self.is_authenticated:
            if await models.User.filter(id=current_user.auth_id, is_admin=True).get_or_none():
                return True
        return False


# NOTE Enables better IDE hints and creating a nice api
current_user: AuthUserEnhanced = quart_auth.current_user


def login_required_if_secured(func: Callable) -> Callable:
    """
    login is required if public access is disabled, otherwise skip
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if await get_system_setting(SystemSettingKeys.PORTAL_SECURED, default=False):
            if not (await current_user.is_authenticated):
                raise quart_auth.Unauthorized()
        return await func(*args, **kwargs)

    return wrapper


# NOTE this is for future updates to web-portal auth
login_standard_required = quart_auth.login_required


def login_admin_required(func: Callable) -> Callable:
    """
    used the same as login_required
    but checks whether user is admin
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not (await current_user.is_authenticated_admin):
            raise quart_auth.Unauthorized()
        return await func(*args, **kwargs)

    return wrapper


def ensure_not_setup(func: Callable) -> Callable:
    """
    used to ensure the app has not gone through setup wizard,
    aborting to 404 if it has.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:

        if await get_system_setting(SystemSettingKeys.HAS_SETUP, default=False):
            abort(404)
        return await func(*args, **kwargs)
    return wrapper
