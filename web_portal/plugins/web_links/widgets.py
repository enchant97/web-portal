from quart import render_template
from web_portal.helpers import PluginMeta

from . import models, views

PLUGIN_META = PluginMeta(
    human_name="web links",
    widgets={"links": "links"},
    db_models=[models],
    blueprints=[views.blueprint],
)


async def render_link_widget(link_ids: tuple[int]) -> str:
    links = await models.Link.filter(id__in=link_ids).all()

    return await render_template(
        "web_links/includes/link-widget.jinja",
        links=links,
    )


async def render_widget(internal_name, config: dict | None) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "links":
            return await render_link_widget(config.get("links", []))
        case _:
            raise ValueError("Unknown widget internal name")
