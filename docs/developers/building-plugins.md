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
First create a folder with your plugin name, following examples will use "my_plugin". This will be used store your plugin package.

For a plugin to work it needs to expose some functionality to web-portal. A `__init__.py` file will allow this to happen. It will need to contain imports of the functions expected by the plugin loader. A list of the required (and optional) variables and function names are shown below:

- PLUGIN_META
- get_settings()
- render_injected_head()
- render_widget()
- render_widget_edit()

## Install Plugin
To install the created plugin simply copy the plugin folder into the plugins directory inside web_portal, this is located at: `web_portal/plugins`. Then start a instance of web-portal, if one was already running it will need to be restarted.
