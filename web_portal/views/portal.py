from quart import Blueprint, flash, redirect, render_template, url_for
from quart_auth import current_user

from ..config import get_settings
from ..database.crud import generate_cached_panels

blueprint = Blueprint("portal", __name__)


@blueprint.route("/")
async def portal():
    if get_settings().PORTAL_SECURED:
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.login"))
    widget_panels = await generate_cached_panels()
    return await render_template(
        "portal.jinja2",
        widget_panels=widget_panels,
    )
