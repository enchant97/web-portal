import asyncio

from quart import Blueprint, flash, redirect, render_template, url_for

from ..core.auth import (current_user, login_admin_required,
                         login_required_if_secured, login_standard_required)
from ..core.constants import PUBLIC_ACCOUNT_USERNAME
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
            "widgets", "widgets__widget", "widgets__widget__plugin")
    if dashboard is None:
        public_account = await models.User.filter(username=PUBLIC_ACCOUNT_USERNAME).get()
        dashboard = (await models.Dashboard.get_or_create(owner=public_account))[0]
        await dashboard.fetch_related("widgets", "widgets__widget", "widgets__widget__plugin")

    rendered_widgets = []

    for dashboard_widget in dashboard.widgets:
        dashboard_widget: models.DashboardWidget
        widget: models.Widget = dashboard_widget.widget
        plugin_name = widget.plugin.internal_name
        widget_name = deconstruct_widget_name(plugin_name, widget.internal_name)
        loaded_plugin = PluginHandler.get_loaded_plugin(plugin_name)

        if loaded_plugin is None:
            # skips loading plugin and warn user
            await flash(
                f"widget with name '{dashboard_widget.name}' could not be loaded, " +
                "please contact administrator",
                "error"
            )
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
            await flash(
                f"widget with name '{dashboard_widget.name}' could not be loaded, " +
                "please contact administrator",
                "error"
            )

    return await render_template(
        "portal.jinja",
        rendered_widgets=rendered_widgets,
    )


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

    await asyncio.gather(
        models.Plugin.filter(internal_name=plugin_name).delete(),
        models.SystemSetting.filter(key__startswith=f"plugin__{plugin_name}").delete()
    )

    await flash("deleted plugin data", "ok")

    return redirect(url_for(".get_plugins_index"))
