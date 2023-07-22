import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from quart import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for)

from web_portal.plugin_api import (current_user, get_widget_details,
                                   get_widget_owner_id, login_admin_required,
                                   login_required_if_secured,
                                   login_standard_required,
                                   redirect_using_back_to, set_widget_config)

from . import models
from .helpers import (VALID_UPLOAD_EXTENSIONS, copy_icons_from_import,
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

    if (suffixes := "".join(Path(file.filename).suffixes)) in VALID_UPLOAD_EXTENSIONS:
        upload_fn = "icons" + suffixes
        with TemporaryDirectory(prefix="web-portal") as temp_location:
            temp_location = Path(temp_location)
            temp_upload_location = temp_location / upload_fn
            await file.save(temp_upload_location)
            extract_upload(temp_upload_location, temp_location)
            upload_stats = copy_icons_from_import(temp_location)

        if upload_stats.png_count == 0 and upload_stats.svg_count == 0:
            await flash("detected no image files, did you put them in the correct format?", "error")
        else:
            await flash(f"uploaded icons (png={upload_stats.png_count}, \
                        svg={upload_stats.svg_count})", "ok")
    else:
        await flash("failed to upload icons, (unknown file extension)", "error")

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


@blueprint.get("/engines/<int:engine_id>/edit")
@login_admin_required
async def get_engines_edit(engine_id: int):
    engine = await models.SearchEngine.get(id=engine_id)

    return await render_template(
        "core/engines/edit.jinja",
        engine=engine,
    )


@blueprint.post("/engines/new")
@login_admin_required
async def post_engines_new():
    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    query_param = form["query-param"].strip()
    method = models.SearchEngineMethod(form["method"].upper())

    if not name:
        await flash("engine name cannot be blank", "error")
        return redirect(url_for(".get_engines_new"))

    await models.SearchEngine.create(
        name=name,
        url=url,
        query_param=query_param,
        method=method,
    )

    await flash(f"created engine with name '{name}'", "ok")

    return redirect(url_for(".get_engines_index"))


@blueprint.post("/engines/<int:engine_id>/edit")
async def post_engines_edit(engine_id: int):
    engine = await models.SearchEngine.get(id=engine_id)

    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    query_param = form["query-param"].strip()
    method = models.SearchEngineMethod(form["method"].upper())

    if not name:
        await flash("engine name cannot be blank", "error")
        return redirect(url_for(".get_engines_edit", engine_id=engine_id))

    engine = engine.update_from_dict(dict(
        name=name,
        url=url,
        query_param=query_param,
        method=method,
    ))

    await engine.save()

    await flash(f"updated engine with name '{name}'", "ok")

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


@blueprint.get("/links/<int:link_id>/edit")
@login_admin_required
async def get_link_edit(link_id: int):
    icon_names = get_icon_names(True)
    link = await models.Link.filter(id=link_id).get()

    return await render_template(
        "core/links/edit.jinja",
        icon_names=icon_names,
        link=link,
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

    if not name:
        await flash("link name cannot be blank", "error")
        return redirect(url_for(".get_link_new"))

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


@blueprint.post("/links/<int:link_id>/edit")
@login_admin_required
async def post_link_edit(link_id: int):
    link = await models.Link.filter(id=link_id).get()

    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    color_name = form["color_name"].strip()
    icon_name = form.get("icon-name")

    if not name:
        await flash("link name cannot be blank", "error")
        return redirect(url_for(".get_link_edit", link_id=link_id))

    if icon_name:
        if get_icon_path(icon_name) is None:
            logger.warning(
                "icon name requested not found, " +
                "or permission to read is missing::name='%s'",
                icon_name,
            )
            await flash("failed to find icon", "error")
            return redirect(url_for(".get_link_edit", link_id=link_id))

    link = link.update_from_dict(dict(
        name=name,
        url=url,
        color_name=color_name,
        icon_name=icon_name,
    ))

    await link.save()

    await flash(f"updated link with name '{name}'", "ok")

    return redirect(url_for(".get_links_index"))


@blueprint.post("/widget/search/<int:widget_id>/update")
@login_standard_required
@redirect_using_back_to
async def post_widget_update_search(widget_id: int):
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    engine_id = (await request.form)["engine-id"]

    engine = await models.SearchEngine.get(id=engine_id)

    widget_details = await get_widget_details(widget_id)

    if widget_details.plugin_name != "core" or \
            widget_details.internal_name != "search":
        abort(400)

    await set_widget_config(widget_id, {"engine_id": engine.id})

    await flash(f"updated search engine to '{engine.name}'", "ok")


@blueprint.post("/widget/links/<int:widget_id>/customise")
@login_standard_required
@redirect_using_back_to
async def post_widget_customise_link(widget_id: int):
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    widget_details = await get_widget_details(widget_id)

    if widget_details.plugin_name != "core" or \
            widget_details.internal_name != "links":
        abort(400)

    widget_config = widget_details.config

    if widget_config is None:
        widget_config = {"links": []}

    is_compact = (await request.form).get("is_compact", False, bool)

    widget_config["is_compact"] = is_compact

    await set_widget_config(widget_id, widget_config)


@blueprint.post("/widget/links/<int:widget_id>/add")
@login_standard_required
@redirect_using_back_to
async def post_widget_add_link(widget_id: int):
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    link_id = int((await request.form)["link-id"])
    link = await models.Link.get(id=link_id)

    widget_details = await get_widget_details(widget_id)

    if widget_details.plugin_name != "core" or \
            widget_details.internal_name != "links":
        abort(400)

    widget_config = widget_details.config

    if widget_config is None:
        widget_config = {"links": []}

    if link_id in widget_config["links"]:
        await flash("not adding link, as already added", "error")
    else:
        widget_config["links"].append(link_id)
        await set_widget_config(widget_id, widget_config)
        await flash(f"added new link '{link.name}' to widget '{widget_details.human_name}'", "ok")


@blueprint.get("/widget/links/<int:widget_id>/<int:link_index>/delete")
@login_standard_required
@redirect_using_back_to
async def get_widget_remove_link(widget_id: int, link_index: int):
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    widget_details = await get_widget_details(widget_id)

    if widget_details.plugin_name != "core" or \
            widget_details.internal_name != "links":
        abort(400)

    widget_config = widget_details.config

    if widget_config is None or len(widget_config.get("links")) < link_index+1:
        await flash("cannot find link to delete", "error")
        return

    widget_config["links"].pop(link_index)

    await set_widget_config(widget_id, widget_config)

    await flash(f"removed link from widget '{widget_details.human_name}'", "ok")
