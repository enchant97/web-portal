from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_auth import current_user
from tortoise.exceptions import IntegrityError

from ..database import models
from ..helpers import is_username_allowed, login_admin_required

blueprint = Blueprint("admin", __name__)


@blueprint.get("/")
@login_admin_required
async def get_index():
    return await render_template("admin/index.jinja")


@blueprint.get("/users/")
@login_admin_required
async def get_users():
    users = await models.User.all()

    return await render_template("admin/users.jinja", users=users)


@blueprint.post("/users/new")
@login_admin_required
async def post_users_new():
    form = await request.form

    username = form["username"].strip()
    password = form["password"]
    is_admin = form.get("is-admin", False, bool)

    if not is_username_allowed(username):
        await flash("Entered username contains invalid characters", "red")
    elif is_admin and len(password) < 12:
        await flash("Password is too short, must be at least 12 characters", "red")
    elif not is_admin and len(password) < 8:
        await flash("Password is too short, must be at least 8 characters", "red")
    elif len(password) > 1024:
        await flash("Password is too long, how would you even remember this?", "red")
    elif password.find(username) != -1:
        await flash("Password cannot contain username", "red")
    else:
        try:
            user = models.User(
                username=username,
                is_admin=is_admin,
            )
            user.set_password(password)
            await user.save()
            await flash(f"created user '{username}'", "green")
        except IntegrityError:
            await flash("Username already taken", "red")

    return redirect(url_for(".get_users"))


@blueprint.get("/users/<int:user_id>/delete")
@login_admin_required
async def get_users_delete(user_id: int):
    if user_id == current_user.auth_id:
        await flash("You cannot delete yourself", "red")
    else:
        await models.User.filter(id=user_id).delete()
        await flash("deleted user", "green")

    return redirect(url_for(".get_users"))


@blueprint.get("/users/<int:user_id>/toggle-admin")
@login_admin_required
async def get_users_toggle_admin(user_id: int):
    if user_id == current_user.auth_id:
        await flash("You cannot change role of yourself", "red")
        return redirect(url_for(".get_users"))

    user = await models.User.filter(id=user_id).get()

    if user.username == "guest":
        await flash("This account cannot become an admin", "red")
        return redirect(url_for(".get_users"))

    user.is_admin = not user.is_admin
    await user.save()

    if user.is_admin:
        await flash("User is now an admin", "green")
    else:
        await flash("User is no longer an admin", "green")

    return redirect(url_for(".get_users"))
