from quart import Blueprint, flash, redirect, render_template, request, url_for
from tortoise.exceptions import IntegrityError

from ..core.auth import ensure_not_setup
from ..core.constants import PUBLIC_ACCOUNT_USERNAME
from ..core.helpers import set_system_setting
from ..core.validation import is_username_allowed
from ..database import models

blueprint = Blueprint("install", __name__, url_prefix="/install")


@blueprint.get("/")
@ensure_not_setup
async def get_index():
    return await render_template("install/index.jinja")


@blueprint.get("/admin-user")
@ensure_not_setup
async def get_admin_user():
    username = request.args.get("username", "")
    return await render_template(
        "install/admin-user.jinja",
        username=username,
    )


@blueprint.post("/admin-user")
@ensure_not_setup
async def post_admin_user():
    form = await request.form

    username = form["username"].strip()
    password = form["password"]
    password_confirm = form["password-confirm"]

    if not is_username_allowed(username):
        await flash("Entered username contains invalid characters", "error")
    elif username == PUBLIC_ACCOUNT_USERNAME:
        await flash("This username is reserved, please use another", "error")
    elif password != password_confirm:
        await flash("Passwords do not match", "error")
    elif len(password) < 12:
        await flash("Password is too short, must be at least 12 characters", "error")
    elif len(password) > 1024:
        await flash("Password is too long, how would you even remember this?", "error")
    elif password.find(username) != -1:
        await flash("Password cannot contain username", "error")
    else:
        try:
            user = models.User(
                username=username,
                is_admin=True,
            )
            user.set_password(password)
            await user.save()

            return redirect(url_for(".get_set_configs"))
        except IntegrityError:
            await flash("Username already taken", "error")

    return redirect(url_for(".get_admin_user", username=username))


@blueprint.get("/configs")
@ensure_not_setup
async def get_set_configs():
    return await render_template(
        "install/config.jinja",
    )


@blueprint.post("/configs")
@ensure_not_setup
async def post_set_configs():
    form = await request.form

    portal_secure = form.get("portal-secure", False, bool)
    show_widget_headers = form.get("show-widget-headers", False, bool)

    await set_system_setting("PORTAL_SECURED", portal_secure)
    await set_system_setting("SHOW_WIDGET_HEADERS", show_widget_headers)

    return redirect(url_for(".get_finish"))


@blueprint.get("/finish")
@ensure_not_setup
async def get_finish():
    await models.SystemSetting.update_or_create(key="has_setup", defaults=dict(value=True))

    return await render_template(
        "install/finish.jinja",
    )
