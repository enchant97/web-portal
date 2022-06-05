from quart import (Blueprint, current_app, flash, redirect, render_template,
                   url_for)
from quart_auth import current_user, login_required

from ..database import models
from ..helpers import PluginHandler, deconstruct_widget_name

blueprint = Blueprint("portal", __name__)


@blueprint.get("/")
async def portal():
    has_setup = await models.SystemSetting.get_or_none(key="has_setup")
    if has_setup is None or has_setup.value is False:
        return redirect(url_for("install.get_index"))

    if current_app.config.get("PORTAL_SECURED"):
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.get_login"))

    user_id =  current_user.auth_id
    dashboard = None

    # load either personal dashboard or 'guest' as a fallback
    if user_id is not None:
        dashboard = await models.Dashboard.get_or_none(owner_id=user_id).prefetch_related(
            "widgets", "widgets__widget", "widgets__widget__plugin")
    if dashboard is None:
        guest = await models.User.filter(username="guest").get()
        dashboard = (await models.Dashboard.get_or_create(owner=guest))[0]
        await dashboard.fetch_related("widgets", "widgets__widget", "widgets__widget__plugin")

    rendered_widgets = []

    # TODO handle either plugin in widget not existing
    for dashboard_widget in dashboard.widgets:
        widget = dashboard_widget.widget
        plugin_name = widget.plugin.internal_name
        widget_name = deconstruct_widget_name(plugin_name, widget.internal_name)
        loaded_plugin = PluginHandler.get_loaded_plugin(plugin_name)
        rendered_widget = await loaded_plugin.module.render_widget(widget_name, dashboard_widget.config)
        rendered_widgets.append((dashboard_widget, rendered_widget))

    return await render_template(
        "portal.jinja",
        rendered_widgets=rendered_widgets,
    )


@blueprint.get("/plugins")
@login_required
async def get_plugins_index():
    loaded_plugins = PluginHandler.get_loaded_plugin_values()

    return await render_template(
        "plugins.jinja",
        loaded_plugins=loaded_plugins,
    )
