from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_auth import current_user, login_required

from ..config import get_settings
from ..database import models
from ..helpers import PluginHandler, deconstruct_widget_name

blueprint = Blueprint("portal", __name__)


@blueprint.route("/")
async def portal():
    if get_settings().PORTAL_SECURED:
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.login"))

    user_id =  current_user.auth_id
    dashboard = None
    is_personal_dash = False

    # load either personal dashboard or 'guest' as a fallback
    if user_id is not None:
        dashboard = await models.Dashboard.get_or_none(owner_id=user_id).prefetch_related(
            "widgets", "widgets__widget", "widgets__widget__plugin")
        if dashboard:
            is_personal_dash = True
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
        "portal.jinja2",
        rendered_widgets=rendered_widgets,
        is_personal_dash=is_personal_dash,
    )


@blueprint.get("/plugins")
@login_required
async def get_plugins_index():
    loaded_plugins = PluginHandler.get_loaded_plugin_values()

    return await render_template(
        "plugins.jinja",
        loaded_plugins=loaded_plugins,
    )


@blueprint.get("/dashboard/edit")
@login_required
async def get_edit_dashboard():
    widgets = await models.Widget.all()
    dashboard = (await models.Dashboard
        .filter(owner_id=current_user.auth_id)
        .get()
    )
    placed_widgets = await dashboard.widgets.all().prefetch_related("widget", "widget__plugin")

    return await render_template(
        "edit.jinja",
        widgets=widgets,
        placed_widgets=placed_widgets,
        get_loaded_plugin=PluginHandler.get_loaded_plugin,
        deconstruct_widget_name=deconstruct_widget_name,
        )


@blueprint.post("/dashboard/add-widget")
@login_required
async def post_add_widget():
    form = await request.form

    name = form["name"].strip()
    widget_id = form["widget-id"]

    dashboard = (await models.Dashboard
        .filter(owner_id=current_user.auth_id)
        .get()
    )

    await models.DashboardWidget.create(
        name=name,
        dashboard=dashboard,
        widget_id=widget_id,
    )

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/widget/<int:widget_id>/delete")
@login_required
async def get_delete_widget(widget_id: int):
    dashboard = (await models.Dashboard
        .filter(owner_id=current_user.auth_id)
        .get()
    )

    await dashboard.widgets.filter(id=widget_id).delete()

    await flash("deleted widget", "green")

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/restore-defaults")
@login_required
async def get_restore_defaults():
    await models.Dashboard.filter(owner_id=current_user.auth_id).delete()
    await flash("Reset dashboard for account", "green")
    return redirect(url_for(".portal"))
