import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from quart import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for)
from web_portal.plugin_api import (PORTAL_ENDPOINT, current_user,
                                   get_plugin_system_setting,
                                   get_widget_details, get_widget_owner_id,
                                   login_admin_required,
                                   login_required_if_secured,
                                   login_standard_required, set_widget_config)

from . import models
from .helpers import (VALID_UPLOAD_EXTENTIONS, copy_icons_from_import,
                      extract_upload, get_icon_names, get_icon_path,
                      get_settings)

logger = logging.getLogger("web-portal")
blueprint = Blueprint("core", __name__, static_folder="static", template_folder="templates")


@blueprint.get("/")
@login_standard_required
async def get_index():
    return await render_template("core/index.jinja")


@blueprint.get("/static/icons/<icon_name>")
@login_required_if_secured
async def get_icon(icon_name):
    full_path = get_icon_path(icon_name)
    if full_path is None:
        abort(404)

    return await send_file(
        full_path,
        attachment_filename=full_path.name
    )


@blueprint.get("/upload-icons")
@login_admin_required
async def get_upload_icons():
    if not get_settings().ALLOW_ICON_UPLOADS:
        await flash("icon upload has been disabled by the admin", "error")
        return redirect(url_for(".get_index"))

    return await render_template("core/upload-icons.jinja")


@blueprint.post("/upload-icons")
@login_admin_required
async def post_upload_icons():
    if not get_settings().ALLOW_ICON_UPLOADS:
        abort(403)

    file = (await request.files)["file"]

    if (suffixes := "".join(Path(file.filename).suffixes)) in VALID_UPLOAD_EXTENTIONS:
        upload_fn = "icons" + suffixes
        with TemporaryDirectory(prefix="web-portal") as temp_location:
            temp_location = Path(temp_location)
            temp_upload_location = temp_location / upload_fn
            await file.save(temp_upload_location)
            extract_upload(temp_upload_location, temp_location)
            copy_icons_from_import(temp_location)

        await flash("uploaded icons", "ok")
    else:
        await flash("failed to upload icons, (unknown file extention)", "error")

    return redirect(url_for(".get_upload_icons"))


@blueprint.get("/engines")
@login_admin_required
async def get_engines_index():
    engines = await models.SearchEngine.all()
    return await render_template(
        "core/engines/index.jinja",
        engines=engines,
    )


@blueprint.get("/engines/new")
@login_admin_required
async def get_engines_new():
    return await render_template("core/engines/new.jinja")


@blueprint.post("/engines/new")
@login_admin_required
async def post_engines_new():
    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    query_param = form["query-param"].strip()
    method = models.SearchEngineMethod(form["method"].upper())

    await models.SearchEngine.create(
        name=name,
        url=url,
        query_param=query_param,
        method=method,
    )

    await flash(f"created engine with name '{name}'", "ok")

    return redirect(url_for(".get_engines_index"))


@blueprint.get("/engines/<int:engine_id>/delete")
@login_admin_required
async def get_engines_delete(engine_id: int):
    await models.SearchEngine.filter(id=engine_id).delete()
    await flash("deleted engine", "ok")

    return redirect(url_for(".get_engines_index"))


@blueprint.get("/links")
@login_admin_required
async def get_links_index():
    links = await models.Link.all()
    return await render_template(
        "core/links/index.jinja",
        links=links
    )


@blueprint.get("/links/new")
@login_admin_required
async def get_link_new():
    icon_names = get_icon_names(True)

    return await render_template(
        "core/links/new.jinja",
        icon_names=icon_names,
    )


@blueprint.get("/links/<int:link_id>/delete")
@login_admin_required
async def get_link_delete(link_id: int):
    await models.Link.filter(id=link_id).delete()
    await flash("deleted link", "ok")

    return redirect(url_for(".get_links_index"))


@blueprint.post("/links/new")
@login_admin_required
async def post_link_new():
    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    color_name = form["color_name"].strip()
    icon_name = form.get("icon-name")

    if icon_name:
        if get_icon_path(icon_name) is None:
            logger.warning(
                "icon name requested not found, " +
                "or permission to read is missing::name='%s'",
                icon_name,
            )
            await flash("failed to find icon", "error")
            return redirect(url_for(".get_link_new"))

    await models.Link.create(
        name=name,
        url=url,
        color_name=color_name,
        icon_name=icon_name,
    )

    await flash(f"created link with name '{name}'", "ok")

    return redirect(url_for(".get_links_index"))


@blueprint.post("/widget/search/<int:widget_id>/update")
@login_standard_required
async def post_widget_update_search(widget_id: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    engine_id = (await request.form)["engine-id"]

    engine = await models.SearchEngine.get(id=engine_id)
    await set_widget_config(widget_id, {"engine_id": engine.id})

    await flash(f"updated search engine to '{engine.name}'", "ok")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))


@blueprint.post("/widget/links/<int:widget_id>/add")
@login_standard_required
async def post_widget_add_link(widget_id: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    link_id = int((await request.form)["link-id"])
    link = await models.Link.get(id=link_id)

    widget_details = await get_widget_details(widget_id)
    widget_config = widget_details.config

    if widget_config is None:
        widget_config = {"links": []}

    if link_id in widget_config["links"]:
        await flash("not adding link, as already added", "error")
    else:
        widget_config["links"].append(link_id)
        await set_widget_config(widget_id, widget_config)
        await flash(f"added new link '{link.name}' to widget '{widget_details.human_name}'", "ok")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))


@blueprint.get("/widget/links/<int:widget_id>/<int:link_index>/delete")
@login_standard_required
async def get_widget_remove_link(widget_id: int, link_index: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    widget_details = await get_widget_details(widget_id)
    widget_config = widget_details.config

    redirect_response = redirect(url_for(PORTAL_ENDPOINT))
    if (back_to_url := request.args.get("back_to")) is not None:
        redirect_response = redirect(back_to_url)

    if widget_config is None or len(widget_config.get("links")) < link_index+1:
        await flash("cannot find link to delete", "error")
        return redirect_response

    widget_config["links"].pop(link_index)

    await set_widget_config(widget_id, widget_config)

    await flash(f"removed link from widget '{widget_details.human_name}'", "ok")

    return redirect_response
