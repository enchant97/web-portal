# flake8: noqa
"""
Unifed plugin api for plugins to access.

Although a plugin could still access other modules,
this module should be recognised
as the supported methods/classes/variables to use by a plugin,
and will be documented in the plugin api manual.
"""

from .core.auth import ensure_not_setup, login_admin_required
from .core.plugin import (PluginMeta, get_plugin_system_setting,
                          remove_plugin_system_setting,
                          set_plugin_system_setting)
from .database import models as app_models
