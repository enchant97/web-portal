from quart import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from web_portal.plugin_api import (PORTAL_ENDPOINT, current_user,
                                   get_widget_details, get_widget_owner_id,
                                   login_standard_required, set_widget_config)

blueprint = Blueprint("core_extras", __name__, template_folder="templates")


@blueprint.get("/")
@login_standard_required
async def get_index():
    return await render_template("core_extras/index.jinja")


@blueprint.post("/widget/embed_html/<int:widget_id>/update")
@login_standard_required
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

    await flash(f"updated HTML content for widget '{widget_details.human_name}'", "ok")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))


@blueprint.post("/widget/iframe/<int:widget_id>/update")
@login_standard_required
async def post_widget_update_iframe(widget_id: int):
    # TODO check widget internal_name to ensure it is valid for this request
    if await get_widget_owner_id(widget_id) != current_user.auth_id:
        abort(401)

    form = await request.form
    iframe_src = form["src"].strip()
    iframe_height = form.get("height", 150, int)

    widget_details = await get_widget_details(widget_id)
    widget_config = widget_details.config
    if widget_config is None:
        widget_config = {"src": ""}

    widget_config["src"] = iframe_src
    widget_config["height"] = iframe_height

    await set_widget_config(widget_id, widget_config)

    await flash(f"updated website url for widget '{widget_details.human_name}'", "ok")

    if (back_to_url := request.args.get("back_to")) is not None:
        return redirect(back_to_url)
    return redirect(url_for(PORTAL_ENDPOINT))
