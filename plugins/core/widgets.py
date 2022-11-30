import asyncio
import logging

from quart import render_template
from web_portal.plugin_api import PluginMeta

from . import models, views
from .helpers import get_settings

logger = logging.getLogger("web-portal")


async def render_widget_link(config: dict) -> str:
    # TODO auto remove links that haven't been found due to deletion
    links = await models.Link.filter(id__in=config.get("links", [])).order_by("name").all()

    return await render_template(
        "core/includes/widgets/link.jinja",
        links=links,
        widget_config=config,
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
            return await render_widget_link(config)
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
        config: dict,
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
        widget_config=config,
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


async def demo_install():
    links = (
        models.Link(
            name="Bitwarden",
            url="",
            color_name="cyan",
            icon_name="bitwarden",
        ),
        models.Link(
            name="Enchanted Code",
            url="https://enchantedcode.co.uk/",
            color_name="green",
        ),
        models.Link(
            name="Router",
            url="",
            color_name="grey",
            icon_name="router",
        ),
        models.Link(
            name="Self Hosted",
            url="",
            color_name="white",
            icon_name="selfhosted",
        ),
        models.Link(
            name="Pihole",
            url="",
            color_name="red",
            icon_name="pihole",
        ),
    )

    engines = (
        models.SearchEngine(
            name="Google",
            url="https://google.com/search",
            query_param="q",
            method=models.SearchEngineMethod.GET,
        ),
        models.SearchEngine(
            name="DuckDuckGo",
            url="https://start.duckduckgo.com/",
            query_param="q",
            method=models.SearchEngineMethod.GET,
        ),
    )

    await asyncio.gather(
        models.Link.bulk_create(links),
        models.SearchEngine.bulk_create(engines),
    )


PLUGIN_META = PluginMeta(
    version_specifier="~= 2.0",
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
    do_demo_setup=demo_install,
)
