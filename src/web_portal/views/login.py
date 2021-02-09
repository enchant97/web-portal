from quart import Blueprint, redirect, render_template, request, url_for
from quart_auth import (AuthUser, Unauthorized, login_required, login_user,
                        logout_user)

from ..database.crud import check_user

blueprint = Blueprint("login", __name__, url_prefix="/")

@blueprint.route("/login", methods=['GET', 'POST'])
async def login():
    if request.method == "POST":
        username = (await request.form)['username']
        password = (await request.form).get('password', '')
        user = await check_user(username, password)
        if user:
            login_user(AuthUser(user.id))
            return redirect(url_for("portal"))

    return await render_template("login.jinja2")

@blueprint.route("/logout")
@login_required
async def logout():
    logout_user()
    return redirect(url_for("portal"))
