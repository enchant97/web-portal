import logging
from quart import Blueprint, flash, redirect, render_template, request, session, url_for
from quart_auth import login_user, logout_user

from ..core.auth import AuthUserEnhanced, current_user, login_standard_required
from ..core.constants import PUBLIC_ACCOUNT_USERNAME, SystemSettingKeys
from ..core.helpers import get_system_setting
from ..database import models

blueprint = Blueprint("login", __name__, url_prefix="/auth")

logger = logging.getLogger("web-portal")

@blueprint.get("/login")
async def get_login():
    if await current_user.is_authenticated:
        # if user is already logged in redirect to portal
        return redirect(url_for("portal.portal"))

    return await render_template("login.jinja")


@blueprint.post("/login")
async def post_login():
    form = await request.form

    username = form["username"]
    password = form["password"]

    # prevents logging in with 'public virtual' account
    if username != PUBLIC_ACCOUNT_USERNAME:
        user = await models.User.filter(username=username).get_or_none()
        if user and user.check_password(password):
            login_user(AuthUserEnhanced(user.id))
            return redirect(url_for("portal.portal"))

    await flash("Username or password incorrect", "error")

    logger.warning("failed login attempt from '%s'", request.remote_addr)

    return redirect(url_for(".get_login"))


@blueprint.get("/logout")
@login_standard_required
async def get_logout():
    logout_user()
    session.clear()

    await flash("You have been logged out", "ok")

    if await get_system_setting(SystemSettingKeys.PORTAL_SECURED, default=False):
        return redirect(url_for(".get_login"))

    return redirect(url_for("portal.portal"))
