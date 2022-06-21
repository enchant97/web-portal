from quart import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from quart_auth import current_user, login_required
from web_portal.plugin_api import (PORTAL_ENDPOINT, get_widget_details,
                                   get_widget_owner_id, login_admin_required,
                                   set_widget_config)

from . import models

blueprint = Blueprint("core", __name__, static_folder="static", template_folder="templates")


@blueprint.get("/")
@login_required
async def get_index():
    return await render_template("core/index.jinja")


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
    return await render_template("core/links/new.jinja")


@blueprint.get("/links/<int:link_id>/delete")
@login_admin_required
async def get_link_delete(link_id: int):
    await models.Link.filter(id=link_id).delete()
    await flash("deleted link", "green")

    return redirect(url_for(".get_links_index"))


@blueprint.post("/links/new")
@login_admin_required
async def post_link_new():
    form = await request.form

    name = form["name"].strip()
    url = form["url"].strip()
    color_name = form["color_name"].strip()

    await models.Link.create(
        name=name,
        url=url,
        color_name=color_name,
    )

    await flash(f"created link with name '{name}'", "green")

    return redirect(url_for(".get_links_index"))


@blueprint.post("/widget/links/<int:widget_id>/add")
@login_required
async def post_widget_add_link(widget_id: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    link_id = (await request.form)["link-id"]
    link = await models.Link.get(id=link_id)

    widget_details = await get_widget_details(widget_id)
    widget_config = widget_details.config

    if widget_config is None:
        widget_config = {"links": []}

    widget_config["links"].append(link_id)

    await set_widget_config(widget_id, widget_config)

    await flash(f"added new link '{link.name}' to widget '{widget_details.human_name}'", "green")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))


@blueprint.post("/widget/embed_html/<int:widget_id>/update")
@login_required
async def post_widget_update_embed_html(widget_id: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    new_content = (await request.form)["content"].strip()

    widget_details = await get_widget_details(widget_id)
    widget_config = widget_details.config
    if widget_config is None:
        widget_config = {"content": ""}

    widget_config["content"] = new_content

    await set_widget_config(widget_id, widget_config)

    await flash(f"updated HTML content for widget '{widget_details.human_name}'", "green")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))
