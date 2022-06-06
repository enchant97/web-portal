"""
Module to assist plugin functionalities
"""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Generator, Optional

from quart import Blueprint

from .helpers import (get_system_setting, remove_system_setting,
                      set_system_setting)


@dataclass
class PluginMeta:
    human_name: str
    widgets: dict[str, str]
    db_models: tuple[str | ModuleType]
    blueprints: tuple[Blueprint]
    plugin_settings: bool
    head_injection: bool
    index_route_url: str


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
            plugin_settings=plugin_meta.plugin_settings,
            head_injection=plugin_meta.head_injection,
            index_route_url=plugin_meta.index_route_url,
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


def make_combined_widget_name(plugin_name: str, widget_name: str) -> str:
    return f"{plugin_name}__{widget_name}"


def deconstruct_widget_name(plugin_name: str, combined_name: str) -> str:
    return combined_name.removeprefix(f"{plugin_name}__")


def make_system_setting_plugin_key(plugin_name: str, key: str) -> str:
    return f"plugin__{plugin_name}_{key}"


async def get_plugin_system_setting(
        plugin_name: str,
        key: str,
        /,
        *,
        default: Optional[Any] = None,
        skip_cache: bool = False) -> Any | None:
    """
    Gets a plugin's system setting stored in db or from cache

        :param plugin_name: The plugin's internal name
        :param key: The setting's key
        :param default: The default value to use if no setting was found, defaults to None
        :param skip_cache: Whether the skip cache and load from db directly, defaults to False
        :return: The loaded value or None
    """
    full_key = make_system_setting_plugin_key(plugin_name, key)
    return get_system_setting(full_key, default, skip_cache)


async def set_plugin_system_setting(plugin_name: str, key: str, value: Any, /):
    """
    Set a plugin's system setting stored in db and updates cache

        :param plugin_name: The plugin's internal name
        :param key: The setting's key
        :param value: Value to update setting to
    """
    full_key = make_system_setting_plugin_key(plugin_name, key)
    await set_system_setting(full_key, value)


async def remove_plugin_system_setting(plugin_name: str, key: str, /):
    """
    Removes a set plugin's system setting stored in db and cache

        :param plugin_name: The plugin's internal name
        :param key: The setting's key
    """
    full_key = make_system_setting_plugin_key(plugin_name, key)
    await remove_system_setting(full_key)