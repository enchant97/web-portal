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
class PluginMeta:
    human_name: str
    widgets: dict[str, str]
    db_models: tuple[str | ModuleType]
    blueprints: tuple[Blueprint]
    head_injection: bool


@dataclass
class LoadedPlugin(PluginMeta):
    internal_name: str
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
        plugin_meta: PluginMeta = imported_module.PLUGIN_META
        return LoadedPlugin(
            human_name=plugin_meta.human_name,
            widgets=plugin_meta.widgets,
            db_models=plugin_meta.db_models,
            blueprints=plugin_meta.blueprints,
            head_injection=plugin_meta.head_injection,
            internal_name=name,
            module=imported_module,
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

    @staticmethod
    def get_loaded_plugin(name: str) -> LoadedPlugin:
        return PluginHandler._loaded_plugins[name]

    @staticmethod
    def get_loaded_plugin_values() -> Generator[LoadedPlugin, None, None]:
        for plugin in PluginHandler._loaded_plugins.values():
            yield plugin


class NotAdmin(Unauthorized):
    pass


class PasswordStrength(ValueError):
    pass


def make_combined_widget_name(plugin_name: str, widget_name: str) -> str:
    return f"{plugin_name}__{widget_name}"


def deconstruct_widget_name(plugin_name: str, combined_name: str) -> str:
    return combined_name.removeprefix(f"{plugin_name}__")


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
