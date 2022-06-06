from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings
from quart import render_template
from web_portal.plugin_api import PluginMeta

from . import models, views

PLUGIN_META = PluginMeta(
    human_name="Core",
    widgets={
        "links": " Links",
        "search": "Web Search",
        },
    db_models=[models],
    blueprints=[views.blueprint],
    plugin_settings = True,
    head_injection = True,
    index_route_url="core.get_index",
)


class PluginSettings(BaseSettings):
    SEARCH_URL: str
    SEARCH_METHOD: Optional[str] = "GET"
    OPEN_TO_NEW_TAB: Optional[bool] = True


@lru_cache
def get_settings():
    return PluginSettings()


async def render_widget_link(link_ids: tuple[int]) -> str:
    links = await models.Link.filter(id__in=link_ids).order_by("name").all()

    return await render_template(
        "core/includes/link-widget.jinja",
        links=links,
    )


async def render_widget(internal_name, config: dict | None) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "links":
            return await render_widget_link(config.get("links", []))
        case "search":
            return await render_template("core/includes/search-widget.jinja")
        case _:
            raise ValueError("Unknown widget internal name")


async def render_widget_edit_link(
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str,
    ) -> str:
    links = await models.Link.all()

    added_links = await models.Link.filter(id__in=config.get("links", [])).all()
    return await render_template(
        "core/includes/link-widget-edit.jinja",
        dash_widget_id=dash_widget_id,
        links=links,
        added_links=added_links,
        back_to_url=back_to_url,
    )


async def render_widget_edit(
        internal_name: str,
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str,
    ) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "links":
            return await render_widget_edit_link(dash_widget_id, config, back_to_url)
        case "search":
            return "No editor available"
        case _:
            raise ValueError("Unknown widget internal name")


async def render_injected_head() -> str:
    return await render_template("core/includes/head.jinja")
