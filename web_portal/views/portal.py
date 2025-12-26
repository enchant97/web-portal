from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

import secrets
from io import BytesIO

from quart import Blueprint, abort, flash, redirect, render_template, send_file, url_for

from ..core.auth import (
    current_user,
    login_admin_required,
    login_required_if_secured,
    login_standard_required,
)
from ..core.config import get_settings
from ..core.constants import DEFAULT_BRANDING, PUBLIC_ACCOUNT_USERNAME, SystemSettingKeys
from ..core.helpers import get_system_setting
from ..core.plugin import PluginHandler, deconstruct_widget_name
from ..database import models

blueprint = Blueprint("portal", __name__, url_prefix="/")


@blueprint.get("/")
@login_required_if_secured
async def portal():
    has_setup = await models.SystemSetting.get_or_none(key="has_setup")
    if has_setup is None or has_setup.value is False:
        return redirect(url_for("install.get_index"))

    user_id = current_user.auth_id
    dashboard = None

    # load either personal dashboard or 'public' as a fallback
    if user_id is not None:
        dashboard = await models.Dashboard.get_or_none(owner_id=user_id).prefetch_related(
            "widgets", "widgets__widget", "widgets__widget__plugin"
        )
    if dashboard is None:
        public_account = await models.User.filter(username=PUBLIC_ACCOUNT_USERNAME).get()
        dashboard = (await models.Dashboard.get_or_create(owner=public_account))[0]
        await dashboard.fetch_related("widgets", "widgets__widget", "widgets__widget__plugin")

    background_image_uid = await dashboard.get_background_image_uids()
    if len(background_image_uid) > 0:
        background_image_uid = secrets.choice(background_image_uid)
    else:
        background_image_uid = None

    rendered_widgets = []
    failed_widgets = []

    for dashboard_widget in dashboard.widgets_sorted():
        dashboard_widget: models.DashboardWidget
        widget: models.Widget = dashboard_widget.widget
        plugin_name = widget.plugin.internal_name
        widget_name = deconstruct_widget_name(plugin_name, widget.internal_name)
        loaded_plugin = PluginHandler.get_loaded_plugin(plugin_name)

        if loaded_plugin is None or loaded_plugin.meta.get_rendered_widget is None:
            # skips loading plugin and warn user
            failed_widgets.append(dashboard_widget.name)
            continue

        try:
            rendered_widget = await loaded_plugin.meta.get_rendered_widget(
                widget_name,
                dashboard_widget.id,
                dashboard_widget.config,
            )
            rendered_widgets.append((dashboard_widget, rendered_widget))
        except ValueError:
            # skips loading widget and warn user
            failed_widgets.append(dashboard_widget.name)

    if failed_widgets:
        await flash(
            f"placed widgets with names {failed_widgets} could not be loaded, "
            "please contact administrator",
            "error",
        )

    return await render_template(
        "portal.jinja",
        branding=await get_system_setting(SystemSettingKeys.BRANDING, default=DEFAULT_BRANDING),
        background_image_uid=background_image_uid,
        rendered_widgets=rendered_widgets,
    )


@blueprint.get("/static/background-images/<uuid:image_uid>")
@login_required_if_secured
async def get_background_image(image_uid: UUID):
    # check if app is setup
    has_setup = await models.SystemSetting.get_or_none(key="has_setup")
    if has_setup is None or has_setup.value is False:
        abort(404)

    user_id = current_user.auth_id
    dashboard = None
    # load either personal dashboard or 'public' as a fallback
    if user_id is not None:
        dashboard = await models.Dashboard.filter(owner_id=user_id).get_or_none().only("id")
    if dashboard is None:
        public_account = await models.User.filter(username=PUBLIC_ACCOUNT_USERNAME).get()
        dashboard = (await models.Dashboard.get_or_create(owner=public_account))[0]
    # get the image
    image = await models.DashboardBackgroundImage.filter(
        uid=image_uid, dashboard_id=dashboard.id
    ).get()
    image_buff = BytesIO(image.content)
    return await send_file(
        image_buff,
        mimetype=image.mimetype,
        cache_timeout=64_000,
    )


@blueprint.get("/static/custom.css")
async def get_custom_css():
    file_path = get_settings().DATA_PATH / "custom.css"

    if not file_path.is_file():
        return ""

    return await send_file(file_path)


@blueprint.get("/plugins")
@login_standard_required
async def get_plugins_index():
    loaded_plugins = PluginHandler.get_loaded_plugin_values()

    missing_plugins = await models.Plugin.filter(
        internal_name__not_in=PluginHandler.get_loaded_plugin_names()
    ).all()

    return await render_template(
        "plugins.jinja",
        loaded_plugins=loaded_plugins,
        missing_plugins=missing_plugins,
    )


@blueprint.get("/admin/plugins/delete-unloaded/<plugin_name>")
@login_admin_required
async def get_delete_plugin_data(plugin_name: str):
    loaded_plugins = PluginHandler.get_loaded_plugin_names()

    if plugin_name in loaded_plugins:
        await flash("cannot delete loaded plugin, unload first", "error")
        return redirect(url_for(".get_plugins_index"))

    await models.Plugin.filter(internal_name=plugin_name).delete()
    await models.SystemSetting.filter(key__startswith=f"plugin__{plugin_name}").delete()

    await flash("deleted plugin data", "ok")

    return redirect(url_for(".get_plugins_index"))
