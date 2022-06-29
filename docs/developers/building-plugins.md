# Building Plugins
This guide is aimed at developers and will aid with the creation of new and amazing custom plugins for web-portal.

## Features
- Easily installable package
- Integrates into a running web-portal instance
- Provide custom placeable widgets
- Widgets included with web-portal are actually a plugin called "core"

## Using The API Module
The API module is a python module that is contained in web-portal that gives plugin developers an easy and unified access to access web-portal.

We can access the plugin api just be importing it like so:

```python
from web_portal import plugin_api
```

The plugin API reference can be accessed [here](plugin-reference.md), which shows what functions are available and how they can be used.

## Plugin Creation
This section will walk-through creating a plugin. Before making a plugin an internal name must be decided, for this tutorial we will use "my_plugin" as that. Please note that the below list is reserved plugin names that cannot be used:

- core
- admin
- install
- login
- portal
- settings

Now a plugin name is chosen let's learn about the format. A plugin in web-portal is just a Python package So we can follow the following standard format:

```
plugin_name/
    __init__.py
    ...
```

For a plugin to be loaded into web-portal; certain functionality will need to be exposed; which is either created in `__init__.py` or imported.

In the current version only one exposure is needed that being the variable `PLUGIN_META`. This however needs to be a very specific object.

As it is preferred to not write code in the `__init__.py` file directly, we can instead import `PLUGIN_META` from a `plugin.py` file which will be contained in the `my_plugin` package.

```python
# filepath: my_plugin/__init__.py
from .plugin import PLUGIN_META
```

Now we must actually create `plugin.py`, which is going to contain all of the plugin's code:

```python
# filepath: my_plugin/plugin.py
from quart import Blueprint, render_template
from quart_auth import login_required
from web_portal import plugin_api

blueprint = Blueprint("my_plugin", __name__, template_folder="templates")


@blueprint.get("/")
@login_required
async def get_index():
    return await render_template("my_plugin/index.jinja")


async def render_widget(
        internal_name: str,
        config: dict | None) -> str:
    return await render_template("my_plugin/my_widget.jinja")


async def render_widget_edit(
        internal_name: str,
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    return "No editor available"


PLUGIN_META = PluginMeta(
    human_name="My Plugin",
    widgets={
        "my_widget": "An amazing widget",
        },
    db_models=[],
    blueprints=[blueprint],
    get_rendered_widget,
    get_rendered_widget_edit,
    # NOTE there are other fields to add more functionality
)

```

The plugin's homepage template:

```jinja
{# filepath: my_plugin/templates/my_plugin/index.jinja #}
{% extends "/shared/base.jinja" %}
{% block title %}My Plugin{% endblock %}
{% block main %}
<p>Welcome to My Plugin!</p>
{% endblock main %}
```

The "my_widget" template:

```jinja
{# filepath: my_plugin/templates/my_plugin/my_widget.jinja #}
<p>This is a really cool widget, that does nothing useful!</p>
```

Now plugin is ready for install.

## Install Plugin
To install the created plugin simply copy the plugin folder into the plugins directory inside web_portal, this is located at: `web_portal/plugins`. Then start a instance of web-portal, if one was already running it will need to be restarted.
