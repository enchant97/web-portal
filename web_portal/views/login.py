from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_auth import login_user, logout_user

from ..core.auth import AuthUserEnhanced, current_user, login_standard_required
from ..database import models

blueprint = Blueprint("login", __name__)


@blueprint.get("/login")
async def get_login():
    if (await current_user.is_authenticated):
        # if user is already logged in redirect to portal
        return redirect(url_for("portal.portal"))

    return await render_template("login.jinja")


@blueprint.post("/login")
async def post_login():
    form = await request.form

    username = form["username"]
    password = form["password"]

    user = await models.User.filter(username=username).get_or_none()

    if user and user.check_password(password):
        login_user(AuthUserEnhanced(user.id))
        return redirect(url_for("portal.portal"))

    await flash("Username or password incorrect", "red")

    return redirect(url_for(".get_login"))


@blueprint.get("/logout")
@login_standard_required
async def get_logout():
    logout_user()

    await flash("You have been logged out", "green")

    return redirect(url_for("portal.portal"))
