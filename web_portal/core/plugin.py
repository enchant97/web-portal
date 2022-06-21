"""
Module to assist plugin functionalities
"""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Generator, Optional

from quart import Blueprint

from ..database import models as app_models
from .config import get_settings
from .helpers import (get_system_setting, remove_system_setting,
                      set_system_setting)


@dataclass
class WidgetDetails:
    human_name: str
    internal_name: str
    plugin_name: str
    config: Any | None


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
        return Path(__file__).parent.parent / "plugins"

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


async def get_widget_owner_id(widget_id: int, /) -> int:
    """
    Get a widget's owner id

        :param widget_id: The widgets id
        :return: The owner id
    """
    widget = await app_models.DashboardWidget.get(id=widget_id).prefetch_related(
        "dashboard"
    )
    return widget.dashboard.owner_id


async def get_widget_details(widget_id: int, /) -> WidgetDetails:
    """
    Get a widgets details

        :param widget_id: The widgets id
        :return: The details
    """
    widget = await app_models.DashboardWidget.get(id=widget_id).prefetch_related(
        "widget",
        "widget__plugin",
    )
    return WidgetDetails(
        widget.name,
        deconstruct_widget_name(
            widget.widget.plugin.internal_name,
            widget.widget.internal_name
        ),
        widget.widget.plugin.internal_name,
        widget.config,
    )


async def set_widget_config(widget_id: int, config: Any | None, /):
    """
    Set a widgets config

        :param widget_id: The widgets id
        :param config: The config to update to
    """
    widget = await app_models.DashboardWidget.get(id=widget_id)
    widget.config = config
    await widget.save()


def get_plugin_data_path(plugin_name: str) -> Path:
    """
    Get a plugins's data path for storing
    persistant data outside of the database,
    path will be created if not exists
    when this function is run

        :param plugin_name: The plugin's internal name
        :return: The data path
    """
    data_path = get_settings().DATA_PATH / "plugins" / plugin_name
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path
