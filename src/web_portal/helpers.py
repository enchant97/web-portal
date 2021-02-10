from functools import wraps
from typing import Any, Callable

from quart_auth import Unauthorized, current_user

from .config import get_settings
from .database.crud import check_is_admin


class NotAdmin(Unauthorized):
    pass


def login_admin_required(func: Callable) -> Callable:
    """
    used the same as login_reqired,
    but checks whether user is admin
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not (await current_user.is_authenticated):
            raise Unauthorized()
        else:
            if not await check_is_admin(current_user.auth_id):
                raise NotAdmin()
            return await func(*args, **kwargs)

    return wrapper
