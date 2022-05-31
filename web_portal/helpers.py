from dataclasses import dataclass
from functools import wraps
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Generator

from quart import Blueprint
from quart_auth import Unauthorized, current_user

from .database.crud import check_is_admin


@dataclass
class LoadedPlugin:
    internal_name: str
    human_name: str
    # internal_name: human_name
    widgets: dict[str, str]
    blueprints: tuple[Blueprint]
    db_models: tuple[str | ModuleType]
    module: ModuleType


class PluginHandler:
    """
    static class for finding/loading plugins
    """
    _loaded_plugins: dict[str, LoadedPlugin] = {}

    @staticmethod
    def get_plugins_path() -> Path:
        return Path(__file__).parent / "plugins"

    @staticmethod
    def get_plugin_names():
        root = PluginHandler.get_plugins_path()
        for path in root.glob("*"):
            if (name := path.name) not in ("__init__.py", "__pycache__") and path.is_dir():
                yield name

    @staticmethod
    def load_plugin(name: str) -> LoadedPlugin:
        imported_module = import_module("." + name, "web_portal.plugins")
        imported_meta = imported_module.Meta
        return LoadedPlugin(
            name,
            imported_meta.human_name,
            imported_meta.widgets,
            imported_meta.blueprints,
            imported_meta.db_models,
            imported_module,
        )

    @staticmethod
    def load_plugins() -> Generator[LoadedPlugin, None, None]:
        for name in PluginHandler.get_plugin_names():
            # TODO add logging here
            # TODO add restricted plugin names
            if name not in PluginHandler._loaded_plugins:
                plugin = PluginHandler.load_plugin(name)
                PluginHandler._loaded_plugins[name] = plugin
                yield plugin

    @staticmethod
    def loaded_plugins() -> dict[LoadedPlugin]:
        return PluginHandler._loaded_plugins


class NotAdmin(Unauthorized):
    pass


class PasswordStrength(ValueError):
    pass


def make_combined_widget_name(plugin_name: str, widget_name: str) -> str:
    return f"{plugin_name}__{widget_name}"


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
