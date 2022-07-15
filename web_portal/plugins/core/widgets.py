import asyncio
import logging

from quart import render_template
from web_portal.plugin_api import PluginMeta

from . import models, views
from .helpers import get_settings

logger = logging.getLogger("web-portal")


async def render_widget_link(link_ids: tuple[int]) -> str:
    # TODO auto remove links that haven't been found due to deletion
    links = await models.Link.filter(id__in=link_ids).order_by("name").all()

    return await render_template(
        "core/includes/widgets/link.jinja",
        links=links,
    )


async def render_widget_search(config: dict) -> str:
    engine_id = config.get("engine_id")

    engine = await models.SearchEngine.get_or_none(id=engine_id)

    if not engine:
        return "No search engine selected..."

    return await render_template(
        "core/includes/widgets/search.jinja",
        engine=engine,
    )


async def render_widget(internal_name, widget_id: int, config: dict | None) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "clock":
            return await render_template("core/includes/widgets/clock.jinja", widget_id=widget_id)
        case "links":
            return await render_widget_link(config.get("links", []))
        case "search":
            return await render_widget_search(config)
        case _:
            logger.error(
                "widget not found in plugin::widget_name='%s',plugin_name='core'",
                internal_name
            )
            raise ValueError("Unknown widget internal name")


async def render_widget_edit_search(
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    engines = await models.SearchEngine.all()

    return await render_template(
        "core/includes/widgets-editor/search.jinja",
        dash_widget_id=dash_widget_id,
        engines=engines,
        curr_engine_id=config.get("engine_id"),
        back_to_url=back_to_url,
    )


async def render_widget_edit_link(
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    links, added_links = await asyncio.gather(
        models.Link.all(),
        models.Link.filter(id__in=config.get("links", [])).all(),
    )

    return await render_template(
        "core/includes/widgets-editor/link.jinja",
        dash_widget_id=dash_widget_id,
        links=links,
        added_links=added_links,
        back_to_url=back_to_url,
    )


async def render_widget_edit(
        internal_name: str,
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "clock":
            return "No editor available"
        case "links":
            return await render_widget_edit_link(dash_widget_id, config, back_to_url)
        case "search":
            return await render_widget_edit_search(dash_widget_id, config, back_to_url)
        case _:
            logger.error(
                "widget not found in plugin::widget_name='%s',plugin_name='core'",
                internal_name
            )
            raise ValueError("Unknown widget internal name")


async def render_injected_head() -> str:
    return await render_template("core/includes/head.jinja")


PLUGIN_META = PluginMeta(
    version_specifier="== 2",
    human_name="Core",
    widgets={
        "clock": "Digital Clock",
        "links": " Links",
        "search": "Web Search",
        },
    db_models=[models],
    blueprints=[views.blueprint],
    index_route_url="core.get_index",
    get_rendered_widget=render_widget,
    get_rendered_widget_edit=render_widget_edit,
    get_settings=get_settings,
    get_injected_head=render_injected_head,
)
