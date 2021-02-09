from quart import Blueprint, request, url_for, redirect, render_template
from quart_auth import login_required

from ..database.crud import get_panel_groups, get_widgets, new_panel_widget, new_panel_group

blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@blueprint.route("/")
@login_required
async def index():
    groups = await get_panel_groups()
    return await render_template("admin.jinja2", groups=groups)

@blueprint.route("/new-widget", methods=["POST"])
@login_required
async def new_widget():
    url = (await request.form)["url"]
    group_id = (await request.form)["group_id"]
    prefix = (await request.form)["prefix"]
    await new_panel_widget(url, prefix, group_id)
    return redirect(url_for("admin.index"))

@blueprint.route("/new-group", methods=["POST"])
@login_required
async def new_group():
    prefix = (await request.form)["prefix"]
    await new_panel_group(prefix)
    return redirect(url_for("admin.index"))
