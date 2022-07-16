"""
Module to assist plugin functionalities
"""
import logging
from collections.abc import Awaitable, Callable, Generator
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Optional

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from quart import Blueprint

from ..database import models as app_models
from .config import get_settings
from .helpers import (get_system_setting, remove_system_setting,
                      set_system_setting)

RESTRICTED_PLUGIN_NAMES = (
    "web_portal",
    "admin",
    "install",
    "login",
    "portal",
    "settings",
    "static",
    "plugin",
)

logger = logging.getLogger("web-portal")


class PluginException(Exception):
    pass


class PluginNameConflictException(PluginException):
    pass


class PluginVersionException(PluginException):
    pass


class PluginRestrictedNameException(PluginException):
    pass


@dataclass
class WidgetDetails:
    """
    Used for storing information about a widget,
    returned by get_widget_details()
    """
    human_name: str
    internal_name: str
    plugin_name: str
    config: Any | None


@dataclass
class PluginMeta:
    """
    Class used when creating a plugin,
    stores all information about a plugin and what it supports.
    """
    version_specifier: str
    human_name: str
    widgets: dict[str, str]
    db_models: tuple[str | ModuleType]
    blueprints: tuple[Blueprint]
    index_route_url: str
    get_rendered_widget: Callable[[str, int, dict | None], Awaitable[str]]
    get_rendered_widget_edit: Callable[[str, int, dict | None, str], Awaitable[str]]
    get_settings: Callable[[], dict] | None = None
    get_injected_head: Callable[[], Awaitable[str]] | None = None
    do_demo_setup: Callable[[], Awaitable] | None = None

    def is_supported_version(self, app_version: str) -> bool:
        """
        Check whether the version requirement matches the given app version

            :param app_version: The app version, given as a semantic version number
            :return: Whether it is supported
        """
        try:
            ver_specifier = SpecifierSet(self.version_specifier)
            return True if app_version in ver_specifier else False
        except InvalidSpecifier:
            raise PluginVersionException(
                "unexpected version specifier, " +
                "please use format from PEP 440 e.g. '== 2'"
            ) from None


@dataclass
class LoadedPlugin:
    internal_name: str
    meta: PluginMeta


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
                logger.debug("found possible plugin::name='%s'", name)
                yield name

    @staticmethod
    def load_plugin(name: str, app_version: str) -> LoadedPlugin:
        imported_module = import_module("." + name, "web_portal.plugins")
        plugin_meta: PluginMeta = imported_module.PLUGIN_META

        # ensure version requested matches app version
        if not plugin_meta.is_supported_version(app_version):
            raise PluginVersionException(
                f"running web-portal=={app_version}, " +
                f"but plugin is wanting web-portal{plugin_meta.version_specifier.strip()}"
            )

        return LoadedPlugin(
            internal_name=name,
            meta=plugin_meta,
        )

    @staticmethod
    def validate_plugin_name(name: str) -> None:
        """
        Raises exceptions if plugin name is invalid

            :param name: The plugin name to test
            :raises PluginRestrictedNameException: Plugin name is not allowed
            :raises PluginNameConflictException: Plugin name detected as already loaded
        """
        if name in RESTRICTED_PLUGIN_NAMES:
            raise PluginRestrictedNameException(f"plugin name '{name}' is restricted")
        if name in PluginHandler._loaded_plugins:
            raise PluginNameConflictException(f"plugin with name '{name}' already loaded")

    @staticmethod
    def load_plugins(app_version: str, skip_list: Iterable[str] = None) -> Generator[LoadedPlugin, None, None]:
        for name in PluginHandler.get_plugin_names():
            if skip_list is not None and name in skip_list:
                logger.info("skipping loading plugin as in skip list::plugin_name='%s'", name)
                continue
            try:
                logger.debug("loading plugin::plugin_name='%s'", name)

                PluginHandler.validate_plugin_name(name)

                plugin = PluginHandler.load_plugin(name, app_version)
                PluginHandler._loaded_plugins[name] = plugin
                logger.debug("loaded plugin::plugin_name='%s'", name)
                yield plugin

            except PluginNameConflictException as err:
                logger.error(
                    "unable to load plugin, " +
                    "plugin with same name already loaded::plugin_name='%s', err='%s'",
                    name, err.args[0]
                )
            except PluginRestrictedNameException as err:
                logger.error(
                    "unable to load plugin, using restricted name::plugin_name='%s', err='%s'",
                    name, err.args[0]
                )
            except PluginVersionException as err:
                logger.error(
                    "unable to load plugin, version incompatible::plugin_name='%s', err='%s'",
                    name, err.args[0]
                )

    @staticmethod
    def loaded_plugins() -> dict[LoadedPlugin]:
        return PluginHandler._loaded_plugins

    @staticmethod
    def get_loaded_plugin(name: str) -> LoadedPlugin | None:
        """
        Gets a loaded plugin by internal name

            :param name: The plugin's internal name
            :return: The loaded plugin, or None if not found
        """
        try:
            return PluginHandler._loaded_plugins[name]
        except KeyError:
            logger.error("plugin is not loaded::plugin_name='%s'", name)

    @staticmethod
    def get_loaded_plugin_values() -> Generator[LoadedPlugin, None, None]:
        for plugin in PluginHandler._loaded_plugins.values():
            yield plugin

    @staticmethod
    def get_loaded_plugin_names() -> list[str]:
        return PluginHandler._loaded_plugins.keys()


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
    return get_system_setting(full_key, default=default, skip_cache=skip_cache)


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
