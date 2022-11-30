import asyncio
import json

from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_auth import login_user
from tortoise.exceptions import IntegrityError

from ..core.auth import AuthUserEnhanced, current_user, login_admin_required
from ..core.config import get_settings
from ..core.constants import PUBLIC_ACCOUNT_USERNAME, SystemSettingKeys
from ..core.helpers import get_system_setting, set_system_setting
from ..core.import_export import Widget_V1, import_v1_widgets
from ..core.validation import check_password, is_username_allowed
from ..database import models

blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@blueprint.get("/")
@login_admin_required
async def get_index():
    return await render_template("admin/index.jinja")


@blueprint.get("/switch-to-public")
@login_admin_required
async def get_switch_to_public():
    public_user = await models.User.filter(username=PUBLIC_ACCOUNT_USERNAME).get().only("id")

    login_user(AuthUserEnhanced(public_user.id))
    await flash(f"switched to {PUBLIC_ACCOUNT_USERNAME} account", "ok")

    return redirect(url_for("portal.portal"))


@blueprint.post("/import-v1-widgets")
@login_admin_required
async def post_import_v1_widgets():
    file = (await request.files)["file"]
    try:
        loaded_json = json.load(file.stream)
        if not isinstance(loaded_json, list):
            raise ValueError()
        widgets = [Widget_V1.parse_obj(widget) for widget in loaded_json]
        count = await import_v1_widgets(widgets)
        if count == -1:
            await flash("Unable to import, are you missing the core plugin?", "error")
        else:
            await flash(f"Imported {count} widgets", "ok")
    except json.JSONDecodeError:
        await flash("failed to parse file, is it valid JSON?", "error")

    return redirect(url_for(".get_index"))


@blueprint.get("/system-settings/")
@login_admin_required
async def get_system_settings():
    public_portal, show_widget_headers = await asyncio.gather(
        get_system_setting(SystemSettingKeys.PORTAL_SECURED, default=False, skip_cache=True),
        get_system_setting(SystemSettingKeys.SHOW_WIDGET_HEADERS, default=False, skip_cache=True),
    )

    # PORTAL_SECURED has a different meaning to public_portal
    public_portal = not public_portal

    has_custom_css = (get_settings().DATA_PATH / "custom.css").is_file()

    return await render_template(
        "admin/system-settings.jinja",
        public_portal=public_portal,
        show_widget_headers=show_widget_headers,
        has_custom_css=has_custom_css,
    )


@blueprint.post("/system-settings/")
@login_admin_required
async def post_system_settings():
    form = await request.form

    portal_secured = not form.get("public-portal", False, bool)
    show_widget_headers = form.get("show-widget-headers", False, bool)

    if not portal_secured and await get_system_setting(SystemSettingKeys.DEMO_MODE, default=False):
        await flash("cannot make portal public when in demo mode", "error")
        return redirect(url_for(".get_system_settings"))

    await asyncio.gather(
        set_system_setting(SystemSettingKeys.PORTAL_SECURED, portal_secured),
        set_system_setting(SystemSettingKeys.SHOW_WIDGET_HEADERS, show_widget_headers),
    )

    await flash("saved system settings", "ok")

    return redirect(url_for(".get_system_settings"))


@blueprint.post("/system-settings/custom-css")
@login_admin_required
async def post_custom_css():
    if await get_system_setting(SystemSettingKeys.DEMO_MODE, default=False):
        await flash("cannot upload custom css in demo mode", "error")
        return redirect(url_for(".get_system_settings"))

    custom_css = (await request.files)["custom-css"]

    await custom_css.save(get_settings().DATA_PATH / "custom.css")

    await flash("uploaded custom css", "ok")

    return redirect(url_for(".get_system_settings"))


@blueprint.get("/system-settings/custom-css/delete")
@login_admin_required
async def get_delete_custom_css():
    if await get_system_setting(SystemSettingKeys.DEMO_MODE, default=False):
        await flash("cannot delete custom css in demo mode", "error")
        return redirect(url_for(".get_system_settings"))

    filepath = get_settings().DATA_PATH / "custom.css"

    if filepath.is_file():
        filepath.unlink()

    return redirect(url_for(".get_system_settings"))


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
        await flash("Entered username contains invalid characters", "error")
    elif (message := check_password(username, password)) is not None:
        await flash(message, "error")
    else:
        try:
            user = models.User(
                username=username,
                is_admin=is_admin,
            )
            user.set_password(password)
            await user.save()
            await flash(f"created user '{username}'", "ok")
        except IntegrityError:
            await flash("Username already taken", "error")

    return redirect(url_for(".get_users"))


@blueprint.get("/users/<int:user_id>/delete")
@login_admin_required
async def get_users_delete(user_id: int):
    user = await models.User.get(id=user_id)

    if user.id == int(current_user.auth_id):
        await flash("You cannot delete yourself", "error")
    elif user.username == PUBLIC_ACCOUNT_USERNAME:
        await flash("You cannot delete the virtual public", "error")
    elif await get_system_setting(SystemSettingKeys.DEMO_MODE, default=False) and \
            user.username in ("admin", "demo"):
        await flash("You cannot delete this user while in demo mode", "error")
    else:
        await models.User.filter(id=user_id).delete()
        await flash("deleted user", "ok")

    return redirect(url_for(".get_users"))


@blueprint.get("/users/<int:user_id>/toggle-admin")
@login_admin_required
async def get_users_toggle_admin(user_id: int):
    if user_id == current_user.auth_id:
        await flash("You cannot change role of yourself", "error")
        return redirect(url_for(".get_users"))

    user = await models.User.filter(id=user_id).get()

    if user.username == PUBLIC_ACCOUNT_USERNAME:
        await flash("This account cannot become an admin", "error")
        return redirect(url_for(".get_users"))
    elif await get_system_setting(SystemSettingKeys.DEMO_MODE, default=False) and \
            user.username in ("admin", "demo"):
        await flash("You cannot change role of user while in demo mode", "error")
        return redirect(url_for(".get_users"))

    user.is_admin = not user.is_admin
    await user.save()

    if user.is_admin:
        await flash("User is now an admin", "ok")
    else:
        await flash("User is no longer an admin", "ok")

    return redirect(url_for(".get_users"))


@blueprint.post("/users/force-login")
@login_admin_required
async def post_user_force_login():
    form = await request.form

    user_id = form["user-id"]
    password = form["password"]

    admin_user = await models.User.get(id=current_user.auth_id).only("password_hash")
    if not admin_user.check_password(password):
        await flash("admin password was incorrect", "error")
        return redirect(url_for(".get_users"))

    user = await models.User.filter(id=user_id, is_admin=False).get_or_none().only("id")

    if user is None:
        await flash("unable to force login as this user", "error")
        return redirect(url_for(".get_users"))

    login_user(AuthUserEnhanced(user.id))
    await flash("forced login to user", "ok")

    return redirect(url_for("portal.portal"))
