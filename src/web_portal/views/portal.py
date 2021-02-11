from quart import Blueprint, flash, redirect, render_template, url_for
from quart_auth import current_user

from ..config import get_settings
from ..database.crud import get_widgets_by_group

blueprint = Blueprint("portal", __name__)

@blueprint.route("/")
async def portal():
    if get_settings().PORTAL_SECURED:
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.login"))
    widgets = await get_widgets_by_group()
    return await render_template(
        "portal.jinja2",
        widgets_grouped=widgets,
        show_panel_headers=get_settings().SHOW_PANEL_HEADERS)

@blueprint.route("/is-alive")
async def is_alive():
    # route to test whether server has not crashed
    return "🆗"
