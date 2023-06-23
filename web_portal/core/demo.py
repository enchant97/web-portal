import asyncio

from tortoise.transactions import atomic

from ..core.constants import SystemSettingKeys
from ..core.helpers import set_system_setting
from ..core.plugin import PluginHandler
from ..database import models


@atomic()
async def do_demo_install():
    admin_user = models.User(
        username="admin",
        is_admin=True,
    )
    admin_user.set_password("admin")

    demo_user = models.User(
        username="demo",
        is_admin=False,
    )
    demo_user.set_password("demo")

    plugins_to_setup = []
    for plugin in PluginHandler.get_loaded_plugin_values():
        if plugin.meta.do_demo_setup is not None:
            plugins_to_setup.append(plugin.meta.do_demo_setup())

    # This is a a lot of asyncio gathering!!!
    await asyncio.gather(
        models.User.bulk_create((admin_user, demo_user)),
        set_system_setting(SystemSettingKeys.PORTAL_SECURED, True),
        set_system_setting(SystemSettingKeys.HAS_SETUP, True),
        set_system_setting(SystemSettingKeys.DEMO_MODE, True),
        *plugins_to_setup,
    )
