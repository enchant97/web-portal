# Building Plugins
This guide is aimed at developers and will aid with the creation of new and amazing custom plugins for web-portal.

## Features
- Easily installable package
- Integrates into a running web-portal instance
- Provide custom placeable widgets
- Widgets included with web-portal are actually a plugin called "core"

## Important Notes
- Web Portal plugins must be compatible with the Python version that it is based on, this is currently 3.10
- Try to make use of asyncio in api async methods this will greatly improve performance
- Try not to use extra pip packages
- Don't override Web Portal internal functions, this will cause instability and may cause damage
- Prefer DRY code, meaning reduce repetition. If it's in the plugin api don't re-invent
- Ensure you always set the min, max app version requirements properly

## Using The API Module
The API module is a python module that is contained in web-portal that gives plugin developers an easy and unified access to access web-portal.

We can access the plugin api just be importing it like so:

```python
from web_portal import plugin_api
```

The plugin API reference can be accessed [here](plugin-reference.md), which shows what functions are available and how they can be used.

## Guidelines Of Making Plugins
To ensure all plugins will integrate with web-portal correctly; when possible use only functionality exposed in the plugin API. For example the following will show a "do" and "don't":

Do:

```python
from quart import Blueprint
from web_portal import plugin_api

blueprint = Blueprint("my_plugin", __name__)

@blueprint.get("/")
@plugin_api.login_standard_required
async def protected_route():
    ...
```

Don't:

```python
from quart import Blueprint
from quart_auth import login_required
from web_portal import plugin_api

blueprint = Blueprint("my_plugin", __name__)

@blueprint.get("/")
@login_required
async def protected_route():
    ...
```

### Using Quart & Quart Auth
As Web Portal plugins will require use of Quart (async implementation of Flask) to register routes and such, take care to ensure you do not access functions that may cause incompatibilities. The following is a list of alternatives (using the plugin api) to use:

- quart.current_app.config
    - get_plugin_system_setting
    - set_plugin_system_setting
    - remove_plugin_system_setting
- quart_auth
    - current_user
    - ensure_not_setup
    - login_admin_required
    - login_required_if_secured
    - login_standard_required

### Using The Database
Web Portal also uses tortoise-orm for databases, you must create models using the class interface and ensure you register them in the PLUGIN_META object. This will also require models to be placed in a separate file from your other plugin code. Forgetting to register them will cause them to not be created or even known to tortoise-orm. To avoid conflict with other plugins and the app please prefix your table names with your plugin name in this format: `<plugin name>__<table name>`.

Model Example:

```python
# filepath: my_plugin/models.py
from tortoise.fields import CharField, IntField
from tortoise.models import Model


class MyModel(Model):
    id = IntField(pk=True)
    name = TextField()

    class Meta:
        table = "my_plugin__my_model"
```

```python
# filepath: my_plugin/...
from . import models

PLUGIN_META = PluginMeta(
    db_models=[models],
    ...
)
```

### Reserved Names
When naming your plugin these names are listed as reserved and must not be used:

- core
- admin
- install
- login
- portal
- settings

### Installing Other Packages
If you are making a plugin and you have installed a package using pip (or another tool), it makes it incompatible with the official Docker image. There are several solutions:

- Create a custom Docker image with the packages added
- Warn users they cannot install the plugin when using Docker
- Copy the package's code into the plugin folder (if the package's license allows)
- Change your code to use the libraries bundles with the official install.

### Version Specifiers
The `version_specifier` in the PLUGIN_META variable takes PEP 440 version specifiers, the following is some examples:

> When specifying a range of versions, it is a good idea to test each version to ensure the plugin works as expected

```
# must be version 2.0.0
== 2.0.0

# must be at least version 2.0, allows for bug fixes e.g. 2.0.3
== 2.0

# must be at least version 2, allows for any update apart from major e.g. 2.10.1
== 2

# must be version 2 up to version 2.5 e.g. 2.3.2 is allowed but 2.6.0 is not
>= 2.0, <= 2.5
```

## Reference Plugin
If you are looking for a example plugin, well your in luck. Web Portal comes with a plugin called "core". You can use this as a good reference on how a plugin should be laid out.

## Plugin Creation
This section will walk-through creating a plugin. Before making a plugin an internal name must be decided, for this tutorial we will use "my_plugin" as that.

Now a plugin name is chosen let's learn about the format. A plugin in web-portal is just a Python package So we can follow the following standard format:

```
plugin_name/
    __init__.py
    templates/plugin_name/
    static/
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
from web_portal import plugin_api

blueprint = Blueprint("my_plugin", __name__, template_folder="templates")


@blueprint.get("/")
@plugin_api.login_standard_required
async def get_index():
    return await render_template("my_plugin/index.jinja")


async def render_widget(
        internal_name: str,
        widget_id: int,
        config: dict | None) -> str:
    return await render_template("my_plugin/my_widget.jinja")


async def render_widget_edit(
        internal_name: str,
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    return "No editor available"


PLUGIN_META = PluginMeta(
    version_specifier="== 2.0",
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
