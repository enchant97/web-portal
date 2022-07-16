import asyncio

from quart import Blueprint, flash, redirect, render_template, request, url_for
from tortoise.exceptions import IntegrityError
from tortoise.transactions import atomic

from ..core.auth import ensure_not_setup
from ..core.constants import PUBLIC_ACCOUNT_USERNAME
from ..core.helpers import set_system_setting
from ..core.plugin import PluginHandler
from ..core.validation import check_password, is_username_allowed
from ..database import models

blueprint = Blueprint("install", __name__, url_prefix="/install")


@blueprint.get("/")
@ensure_not_setup
async def get_index():
    return await render_template("install/index.jinja")


@blueprint.get("/demo-install")
@ensure_not_setup
@atomic()
async def get_demo_install():
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

    return redirect(url_for("login.get_login"))


@blueprint.get("/admin-user")
@ensure_not_setup
async def get_admin_user():
    username = request.args.get("username", "")
    return await render_template(
        "install/admin-user.jinja",
        username=username,
    )


@blueprint.post("/admin-user")
@ensure_not_setup
async def post_admin_user():
    form = await request.form

    username = form["username"].strip()
    password = form["password"]
    password_confirm = form["password-confirm"]

    if not is_username_allowed(username):
        await flash("Entered username contains invalid characters", "error")
    elif username == PUBLIC_ACCOUNT_USERNAME:
        await flash("This username is reserved, please use another", "error")
    elif (message := check_password(username, password, password_confirm)) is not None:
        await flash(message.value, "error")
    else:
        try:
            user = models.User(
                username=username,
                is_admin=True,
            )
            user.set_password(password)
            await user.save()

            return redirect(url_for(".get_set_configs"))
        except IntegrityError:
            await flash("Username already taken", "error")

    return redirect(url_for(".get_admin_user", username=username))


@blueprint.get("/configs")
@ensure_not_setup
async def get_set_configs():
    return await render_template(
        "install/config.jinja",
    )


@blueprint.post("/configs")
@ensure_not_setup
async def post_set_configs():
    form = await request.form

    portal_secured = not form.get("public-portal", False, bool)
    show_widget_headers = form.get("show-widget-headers", False, bool)

    await asyncio.gather(
        set_system_setting("PORTAL_SECURED", portal_secured),
        set_system_setting("SHOW_WIDGET_HEADERS", show_widget_headers),
    )

    return redirect(url_for(".get_finish"))


@blueprint.get("/finish")
@ensure_not_setup
async def get_finish():
    await models.SystemSetting.update_or_create(key="has_setup", defaults=dict(value=True))

    return await render_template(
        "install/finish.jinja",
    )
