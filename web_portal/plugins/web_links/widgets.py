from quart import render_template

from web_portal.database import models as app_models
from . import models


async def render_link_widget(widget: app_models.DashboardWidget) -> str:
    link_ids = widget.config["links"]

    links = await models.Link.filter(id__in=link_ids).all()

    return await render_template(
        "web_links/includes/link-widget.jinja",
        links=links,
    )


async def render_widget(widget: app_models.DashboardWidget) -> str:
    # HACK: this should select the widget to load not assume it's a 'link'
    return await render_link_widget(widget)
