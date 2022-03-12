import json
import logging

from quart import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from tortoise.exceptions import DoesNotExist, IntegrityError

from ..database import crud
from ..helpers import PasswordStrength, login_admin_required
from ..import_export import Widget_V1, export_to_v1_widgets, import_v1_widgets

blueprint = Blueprint("admin", __name__)


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
    try:
        url = (await request.form)["url"]
        group_id = (await request.form)["group_id"]
        if not group_id.isnumeric():
            await flash("form field type error", "red")
        else:
            prefix = (await request.form)["prefix"]
            color_name = (await request.form)["color_name"]
            await crud.new_panel_widget(url, prefix, color_name, group_id)
            await flash("created new widget", "green")
    except IntegrityError:
        logging.exception("new_widget IntegrityError")
        await flash("form field id's are invalid", "red")
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
    try:
        widget_id = (await request.form)["widget_id"]
        group_id = (await request.form)["group_id"]
        if not widget_id.isnumeric() or not group_id.isnumeric():
            await flash("form field type error", "red")
        else:
            await crud.modify_widget_group(widget_id, group_id)
            await flash("changed widget group", "green")
    except IntegrityError:
        logging.exception("new_widget IntegrityError")
        await flash("form field id's are invalid", "red")
    return redirect(url_for("admin.index"))


@blueprint.route("/delete-widget", methods=["POST"])
@login_admin_required
async def delete_widget():
    widget_id = (await request.form)["widget_id"]
    if not widget_id.isnumeric():
        await flash("form field type error", "red")
    else:
        await crud.delete_widget_by_id(widget_id)
        await flash("deleted widget", "green")
    return redirect(url_for("admin.index"))


@blueprint.route("/change-widget-color", methods=["POST"])
@login_admin_required
async def change_widget_color():
    widget_id = (await request.form)["widget_id"]
    color_name = (await request.form)["color_name"]
    if not widget_id.isnumeric():
        await flash("form field type error", "red")
    else:
        await crud.modify_widget_color(widget_id, color_name)
        await flash("changed widget color", "green")
    return redirect(url_for("admin.index"))


@blueprint.route("/change-widget-url", methods=["POST"])
@login_admin_required
async def change_widget_url():
    widget_id = (await request.form)["widget_id"]
    url = (await request.form)["url"]
    if not widget_id.isnumeric():
        await flash("form field type error", "red")
    else:
        await crud.modify_widget_url(widget_id, url)
        await flash("changed widget url", "green")
    return redirect(url_for("admin.index"))


@blueprint.route("/new-user", methods=["POST"])
@login_admin_required
async def new_user():
    try:
        username = (await request.form)["username"]
        password = (await request.form)["password"]
        if len(password) < 8:
            raise PasswordStrength("password less than 8 characters")
        is_admin = (await request.form).get("is_admin", False, bool)
        await crud.new_user(username, password, is_admin)
        await flash("created new user", "green")
    except PasswordStrength as err:
        await flash(err.args[0], "red")
    return redirect(url_for("admin.index"))


@blueprint.route("/delete-user", methods=["POST"])
@login_admin_required
async def delete_user():
    user_id = (await request.form)["user_id"]
    if not user_id.isnumeric():
        await flash("form field type error", "red")
    else:
        await crud.delete_user(user_id)
        await flash("deleted user", "green")
    return redirect(url_for("admin.index"))


@blueprint.route("/modify-user-permissions", methods=["POST"])
@login_admin_required
async def modify_user_permissions():
    user_id = (await request.form)["user_id"]
    is_admin = (await request.form).get("is_admin", False, bool)
    if not user_id.isnumeric():
        await flash("form field type error", "red")
    else:
        await crud.modify_user_permissions(user_id, is_admin)
        await flash("modified permissions", "green")
    return redirect(url_for("admin.index"))


@blueprint.route("/change-password", methods=["POST"])
@login_admin_required
async def change_user_password():
    try:
        user_id = (await request.form)["user_id"]
        new_password = (await request.form)["new_password"]
        if len(new_password) < 8:
            raise PasswordStrength("password less than 8 characters")
        if not user_id.isnumeric():
            await flash("form field type error", "red")
        else:
            await crud.modify_user_password(user_id, new_password)
            await flash("changed password", "green")
    except DoesNotExist:
        logging.exception("row with id not found")
        await flash("user does not exist with given id", "red")
    except PasswordStrength as err:
        await flash(err.args[0], "red")
    return redirect(url_for("admin.index"))


@blueprint.get("/export/v1")
@login_admin_required
async def get_export_v1_widgets():
    widgets = [widget.dict() async for widget in export_to_v1_widgets()]
    return jsonify(widgets)


@blueprint.post("/import/v1")
@login_admin_required
async def post_import_v1_widgets():
    file = (await request.files)["file"]
    loaded_json = json.load(file.stream)
    if not isinstance(loaded_json, list):
        raise ValueError()
    widgets = [Widget_V1.parse_obj(widget) for widget in loaded_json]
    await import_v1_widgets(widgets)
    await flash("Importing widgets", "green")
    return redirect(url_for("admin.index"))
