from quart import Blueprint, redirect, render_template, request, url_for

from ..database import crud
from ..helpers import login_admin_required

blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@blueprint.route("/")
@login_admin_required
async def index():
    groups = await crud.get_panel_groups()
    widgets = await crud.get_widgets()
    return await render_template("admin.jinja2", groups=groups, widgets=widgets)

@blueprint.route("/new-widget", methods=["POST"])
@login_admin_required
async def new_widget():
    url = (await request.form)["url"]
    group_id = (await request.form)["group_id"]
    prefix = (await request.form)["prefix"]
    color_name = (await request.form)["color_name"]
    await crud.new_panel_widget(url, prefix, color_name, group_id)
    return redirect(url_for("admin.index"))

@blueprint.route("/new-group", methods=["POST"])
@login_admin_required
async def new_group():
    prefix = (await request.form)["prefix"]
    await crud.new_panel_group(prefix)
    return redirect(url_for("admin.index"))

@blueprint.route("/re-goup-widget", methods=["POST"])
@login_admin_required
async def re_group_widget():
    widget_id = (await request.form)["widget_id"]
    group_id = (await request.form)["group_id"]
    await crud.modify_widget_group(widget_id, group_id)
    return redirect(url_for("admin.index"))

@blueprint.route("/delete-widget", methods=["POST"])
@login_admin_required
async def delete_widget():
    widget_id = (await request.form)["widget_id"]
    await crud.delete_widget_by_id(widget_id)
    return redirect(url_for("admin.index"))

@blueprint.route("/change-widget-color", methods=["POST"])
@login_admin_required
async def change_widget_color():
    widget_id = (await request.form)["widget_id"]
    color_name = (await request.form)["color_name"]
    await crud.modify_widget_color(widget_id, color_name)
    return redirect(url_for("admin.index"))
