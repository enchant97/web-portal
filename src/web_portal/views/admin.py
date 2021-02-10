from quart import Blueprint, redirect, render_template, request, url_for, flash

from ..database import crud
from ..helpers import login_admin_required

blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@blueprint.route("/")
@login_admin_required
async def index():
    groups = await crud.get_panel_groups()
    widgets = await crud.get_widgets()
    users = await crud.get_users()
    return await render_template(
        "admin.jinja2",
        groups=groups,
        widgets=widgets,
        users=users)

@blueprint.route("/new-widget", methods=["POST"])
@login_admin_required
async def new_widget():
    url = (await request.form)["url"]
    group_id = (await request.form)["group_id"]
    prefix = (await request.form)["prefix"]
    color_name = (await request.form)["color_name"]
    await crud.new_panel_widget(url, prefix, color_name, group_id)
    await flash("created new widget", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/new-group", methods=["POST"])
@login_admin_required
async def new_group():
    prefix = (await request.form)["prefix"]
    await crud.new_panel_group(prefix)
    await flash("created new widget group", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/re-goup-widget", methods=["POST"])
@login_admin_required
async def re_group_widget():
    widget_id = (await request.form)["widget_id"]
    group_id = (await request.form)["group_id"]
    await crud.modify_widget_group(widget_id, group_id)
    await flash("changed widget group", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/delete-widget", methods=["POST"])
@login_admin_required
async def delete_widget():
    widget_id = (await request.form)["widget_id"]
    await crud.delete_widget_by_id(widget_id)
    await flash("deleted widget", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/change-widget-color", methods=["POST"])
@login_admin_required
async def change_widget_color():
    widget_id = (await request.form)["widget_id"]
    color_name = (await request.form)["color_name"]
    await crud.modify_widget_color(widget_id, color_name)
    await flash("changed widget color", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/new-user", methods=["POST"])
@login_admin_required
async def new_user():
    username = (await request.form)["username"]
    password = (await request.form)["password"]
    is_admin = (await request.form).get("is_admin", False, bool)
    await crud.new_user(username, password, is_admin)
    await flash("created new user", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/delete-user", methods=["POST"])
@login_admin_required
async def delete_user():
    user_id = (await request.form)["user_id"]
    await crud.delete_user(user_id)
    await flash("deleted user", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/modify-user-permissions", methods=["POST"])
@login_admin_required
async def modify_user_permissions():
    user_id = (await request.form)["user_id"]
    is_admin = (await request.form).get("is_admin", False, bool)
    await crud.modify_user_permissions(user_id, is_admin)
    await flash("modified permissions", "green")
    return redirect(url_for("admin.index"))

@blueprint.route("/change-password", methods=["POST"])
@login_admin_required
async def change_user_password():
    user_id = (await request.form)["user_id"]
    new_password = (await request.form)["new_password"]
    await crud.modify_user_password(user_id, new_password)
    await flash("changed password", "green")
    return redirect(url_for("admin.index"))
