"""
Module to assist with authentication
"""

from functools import wraps
from typing import Any, Callable

from quart import abort
from quart_auth import AuthUser, Unauthorized, current_user

from ..database import models
from .helpers import get_system_setting


class AuthUserEnhanced(AuthUser):
    @property
    async def is_authenticated_admin(self):
        if await self.is_authenticated:
            if await models.User.filter(id=current_user.auth_id, is_admin=True).get_or_none():
                return True
        return False


def login_admin_required(func: Callable) -> Callable:
    """
    used the same as login_reqired,
    but checks whether user is admin
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not (await current_user.is_authenticated_admin):
            raise Unauthorized()
        return await func(*args, **kwargs)

    return wrapper


def ensure_not_setup(func: Callable) -> Callable:
    """
    used to ensure the app has not gone through setup wizard,
    aborting to 404 if it has.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:

        if await get_system_setting("has_setup", False) is True:
            abort(404)
        return await func(*args, **kwargs)
    return wrapper
