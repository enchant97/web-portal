"""
Unifed plugin api for plugins to access.

Although a plugin could still access other modules,
this module should be recognised
as the supported methods/classes/variables to use by a plugin,
and will be documented in the plugin api manual.
"""

from .core.auth import ensure_not_setup, login_admin_required
from .core.plugin import (PluginMeta, WidgetDetails, get_plugin_data_path,
                          get_plugin_system_setting, get_widget_details,
                          get_widget_owner_id, remove_plugin_system_setting,
                          set_plugin_system_setting, set_widget_config)

PORTAL_ENDPOINT = "portal.portal"
