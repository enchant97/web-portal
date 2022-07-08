from quart import Blueprint, flash, redirect, render_template, request, url_for

from ..core.auth import current_user, login_standard_required
from ..core.plugin import PluginHandler, deconstruct_widget_name
from ..database import models

blueprint = Blueprint("settings", __name__, url_prefix="/settings")


@blueprint.get("/")
@login_standard_required
async def get_index():
    dashboard = await models.Dashboard.get_or_none(owner_id=current_user.auth_id)

    return await render_template(
        "settings/index.jinja",
        is_personal_dash=True if dashboard else False,
    )


@blueprint.get("/dashboard/edit")
@login_standard_required
async def get_edit_dashboard():
    widgets = await models.Widget.all()
    dashboard, is_new_dash = await models.Dashboard.get_or_create(owner_id=current_user.auth_id)
    placed_widgets = await dashboard.widgets.all()

    if is_new_dash:
        await flash("Created new dashboard", "ok")

    return await render_template(
        "settings/dashboard-edit.jinja",
        widgets=widgets,
        placed_widgets=placed_widgets,
    )


@blueprint.post("/dashboard/widget/add")
@login_standard_required
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


@blueprint.get("/dashboard/<int:widget_id>/edit")
@login_standard_required
async def get_edit_dashboard_widget(widget_id: int):
    dashboard = await models.Dashboard.get(owner_id=current_user.auth_id)
    widget = (await dashboard.widgets.filter(id=widget_id)
                     .get()
                     .prefetch_related("widget", "widget__plugin")
                     )

    return await render_template(
        "settings/dashboard-widget-edit.jinja",
        widget=widget,
        get_loaded_plugin=PluginHandler.get_loaded_plugin,
        deconstruct_widget_name=deconstruct_widget_name,
    )


@blueprint.get("/dashboard/widget/<int:widget_id>/delete")
@login_standard_required
async def get_delete_widget(widget_id: int):
    dashboard = (await models.Dashboard
                 .filter(owner_id=current_user.auth_id)
                 .get()
                 )

    await dashboard.widgets.filter(id=widget_id).delete()

    await flash("deleted widget", "ok")

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/restore-defaults")
@login_standard_required
async def get_restore_defaults():
    await models.Dashboard.filter(owner_id=current_user.auth_id).delete()
    await flash("Reset dashboard for account", "ok")
    return redirect(url_for(".get_index"))
