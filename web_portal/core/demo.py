import asyncio

from tortoise.transactions import atomic

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

    await asyncio.gather(
        models.User.bulk_create((admin_user, demo_user)),
        set_system_setting("PORTAL_SECURED", True),
        set_system_setting("SHOW_WIDGET_HEADERS", True),
        models.SystemSetting.update_or_create(key="has_setup", defaults=dict(value=True)),
    )

    for plugin in PluginHandler.get_loaded_plugin_values():
        if plugin.meta.do_demo_setup is not None:
            await plugin.meta.do_demo_setup()

    await set_system_setting("DEMO_MODE", True)
