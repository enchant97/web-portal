from quart import Blueprint, flash, redirect, render_template, url_for
from quart_auth import current_user

from ..config import get_settings

# HACK
from web_portal.plugins.web_links.widgets import render_widget
from ..database import models

blueprint = Blueprint("portal", __name__)


@blueprint.route("/")
async def portal():
    if get_settings().PORTAL_SECURED:
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.login"))

    # HACK
    rendered_widgets = []
    widget = await models.DashboardWidget.first()
    if widget is not None:
        rendered_widgets.append((widget, await render_widget(widget)))

    return await render_template(
        "portal.jinja2",
        rendered_widgets=rendered_widgets,
    )
