from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_auth import current_user, login_required, login_user, logout_user

from ..database.crud import check_user
from ..helpers import AuthUserEnhanced

blueprint = Blueprint("login", __name__)

@blueprint.route("/login", methods=['GET', 'POST'])
async def login():
    if request.method == "POST":
        username = (await request.form)['username']
        password = (await request.form).get('password', '')
        user = await check_user(username, password)
        if user:
            login_user(AuthUserEnhanced(user.id))
            return redirect(url_for("portal.portal"))
        await flash("username or password incorrect", "red")

    if (await current_user.is_authenticated):
        # if user is already logged in redirect to portal
        return redirect(url_for("portal.portal"))

    return await render_template("login.jinja2")

@blueprint.route("/logout")
@login_required
async def logout():
    logout_user()
    await flash("You have been logged out", "green")
    return redirect(url_for("portal.portal"))
