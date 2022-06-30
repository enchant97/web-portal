# Plugin API Reference
This page shows the available public API available for plugins to access.

You can access them by importing them like this:

```python
from web_portal.plugin_api import login_admin_required

# Or

from web_portal import plugin_api
```

## Variables
::: web_portal.plugin_api.current_user

## Route Decorators
::: web_portal.plugin_api.ensure_not_setup
::: web_portal.plugin_api.login_admin_required
::: web_portal.plugin_api.login_required_if_secured
::: web_portal.plugin_api.login_standard_required

## Settings Access
::: web_portal.plugin_api.get_plugin_system_setting
::: web_portal.plugin_api.set_plugin_system_setting
::: web_portal.plugin_api.remove_plugin_system_setting

## Widget Access
::: web_portal.plugin_api.WidgetDetails
::: web_portal.plugin_api.get_widget_owner_id
::: web_portal.plugin_api.get_widget_details
::: web_portal.plugin_api.set_widget_config

## Plugin
::: web_portal.plugin_api.PluginMeta
::: web_portal.plugin_api.get_plugin_data_path

## Endpoints
::: web_portal.plugin_api.PORTAL_ENDPOINT
