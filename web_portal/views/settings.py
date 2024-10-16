import asyncio
import logging

from quart import Blueprint, flash, redirect, render_template, request, session, url_for
from quart_auth import logout_user

from ..core.auth import current_user, login_standard_required
from ..core.plugin import PluginHandler, deconstruct_widget_name
from ..core.validation import check_password
from ..database import models

blueprint = Blueprint("settings", __name__, url_prefix="/settings")

logger = logging.getLogger("web-portal")


@blueprint.get("/")
@login_standard_required
async def get_index():
    user, dashboard = await asyncio.gather(
        models.User.get(id=current_user.auth_id),
        models.Dashboard.get_or_none(owner_id=current_user.auth_id),
    )

    return await render_template(
        "settings/index.jinja",
        user=user,
        is_personal_dash=bool(dashboard),
    )


@blueprint.get("/account")
@login_standard_required
async def get_user_account():
    return await render_template("settings/account.jinja")


@blueprint.post("/account/change-password")
@login_standard_required
async def post_change_password():
    user, form = await asyncio.gather(
        models.User.get(id=current_user.auth_id),
        request.form,
    )

    current_password = form["current-password"]
    new_password = form["new-password"]
    confirm_new_password = form["confirm-new-password"]

    if new_password != confirm_new_password:
        await flash("new passwords do not match", "error")
        return redirect(url_for(".get_user_account"))
    if (message := check_password(user.username, new_password)) is not None:
        await flash(message, "error")
        return redirect(url_for(".get_user_account"))
    if not user.check_password(current_password):
        await flash("your current password is not valid", "error")
        logger.warning("failed change password attempt from '%s'", request.remote_addr)
        return redirect(url_for(".get_user_account"))
    user.set_password(new_password)
    await user.save()
    logout_user()
    session.clear()
    await flash("password changed. You have been logged out", "ok")
    return redirect(url_for("login.get_login"))


@blueprint.get("/dashboard/edit")
@login_standard_required
async def get_edit_dashboard():
    widgets = await models.Widget.all()
    dashboard, is_new_dash = await models.Dashboard.get_or_create(owner_id=current_user.auth_id)
    await dashboard.fetch_related("widgets")
    placed_widgets = dashboard.widgets_sorted()

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

    if not name:
        await flash("widget name cannot be blank", "error")
        return redirect(url_for(".get_edit_dashboard"))

    dashboard = await models.Dashboard.filter(owner_id=current_user.auth_id).get()

    await dashboard.append_widget(
        models.DashboardWidget(
            name=name,
            dashboard=dashboard,
            widget_id=widget_id,
        )
    )

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/<int:widget_id>/edit")
@login_standard_required
async def get_edit_dashboard_widget(widget_id: int):
    dashboard = await models.Dashboard.get(owner_id=current_user.auth_id)
    widget = (
        await dashboard.widgets.filter(id=widget_id)
        .get()
        .prefetch_related("widget", "widget__plugin")
    )

    loaded_plugin = PluginHandler.get_loaded_plugin(widget.widget.plugin.internal_name)

    if loaded_plugin is None or loaded_plugin.meta.get_rendered_widget_edit is None:
        await flash("Editor could not be loaded, please contact administrator", "error")
        return redirect(url_for(".get_edit_dashboard"))

    widget_name = deconstruct_widget_name(
        widget.widget.plugin.internal_name,
        widget.widget.internal_name,
    )
    back_url = url_for(".get_edit_dashboard_widget", widget_id=widget.id)

    try:
        rendered_editor = await loaded_plugin.meta.get_rendered_widget_edit(
            widget_name,
            widget.id,
            widget.config,
            back_url,
        )

        return await render_template(
            "settings/dashboard-widget-edit.jinja",
            widget=widget,
            rendered_editor=rendered_editor,
        )
    except ValueError:
        await flash("Editor could not be loaded, please contact administrator", "error")
        return redirect(url_for(".get_edit_dashboard"))


@blueprint.post("/dashboard/<int:widget_id>/edit")
@login_standard_required
async def post_edit_dashboard_widget(widget_id: int):
    dashboard = await models.Dashboard.get(owner_id=current_user.auth_id)
    widget: models.DashboardWidget = await dashboard.widgets.filter(id=widget_id).get()

    form = await request.form

    widget_name = form["name"].strip()
    show_header = form.get("show-header", False, bool)

    if not widget_name:
        await flash("widget name cannot be blank", "error")
        return redirect(url_for(".get_edit_dashboard_widget", widget_id=widget_id))

    widget.name = widget_name
    widget.show_header = show_header
    await widget.save()

    await flash("updated widget", "ok")

    return redirect(url_for(".get_edit_dashboard_widget", widget_id=widget_id))


@blueprint.get("/dashboard/widget/<int:widget_id>/shift-left")
@login_standard_required
async def get_widget_shift_left(widget_id: int):
    dashboard = (
        await models.Dashboard.filter(owner_id=current_user.auth_id)
        .prefetch_related("widgets")
        .get()
    )
    await dashboard.shift_widget_left(widget_id)

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/widget/<int:widget_id>/shift-right")
@login_standard_required
async def get_widget_shift_right(widget_id: int):
    dashboard = (
        await models.Dashboard.filter(owner_id=current_user.auth_id)
        .prefetch_related("widgets")
        .get()
    )
    await dashboard.shift_widget_right(widget_id)

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/widget/<int:widget_id>/delete")
@login_standard_required
async def get_delete_widget(widget_id: int):
    dashboard = await models.Dashboard.filter(owner_id=current_user.auth_id).get()

    await dashboard.pop_widget_by_id(widget_id)

    await flash("deleted widget", "ok")

    return redirect(url_for(".get_edit_dashboard"))


@blueprint.get("/dashboard/restore-defaults")
@login_standard_required
async def get_restore_defaults():
    await models.Dashboard.filter(owner_id=current_user.auth_id).delete()
    await flash("Reset dashboard for account", "ok")
    return redirect(url_for(".get_index"))
