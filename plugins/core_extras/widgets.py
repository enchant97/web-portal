import logging

from quart import render_template
from web_portal.plugin_api import PluginMeta

from . import views

logger = logging.getLogger("web-portal")


async def render_widget_iframe(config: dict) -> str:
    iframe_src = config.get("src")
    iframe_height = config.get("height", 150)

    return await render_template(
        "core_extras/includes/widgets/iframe.jinja",
        iframe_src=iframe_src,
        iframe_height=iframe_height,
    )


async def render_widget(internal_name, widget_id: int, config: dict | None) -> str:
    if config is None:
        config = {}
    match internal_name:
        case "embed_html":
            return config.get("content", "")
        case "iframe":
            return await render_widget_iframe(config)
        case _:
            logger.error(
                "widget not found in plugin::widget_name='%s',plugin_name='core_extras'",
                internal_name
            )
            raise ValueError("Unknown widget internal name")


async def render_widget_edit_embed_html(
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    content = config.get("content", "")

    return await render_template(
        "core_extras/includes/widgets-editor/embed_html.jinja",
        content=content,
        dash_widget_id=dash_widget_id,
        back_to_url=back_to_url,
    )


async def render_widget_edit_iframe(
        dash_widget_id: int,
        config: dict | None,
        back_to_url: str) -> str:
    iframe_src = config.get("src", "")
    iframe_height = config.get("height", 150)

    return await render_template(
        "core_extras/includes/widgets-editor/iframe.jinja",
        iframe_src=iframe_src,
        iframe_height=iframe_height,
        dash_widget_id=dash_widget_id,
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
        case "embed_html":
            return await render_widget_edit_embed_html(dash_widget_id, config, back_to_url)
        case "iframe":
            return await render_widget_edit_iframe(dash_widget_id, config, back_to_url)
        case _:
            logger.error(
                "widget not found in plugin::widget_name='%s',plugin_name='core_extras'",
                internal_name
            )
            raise ValueError("Unknown widget internal name")


PLUGIN_META = PluginMeta(
    version_specifier="== 2",
    human_name="Core-Extras",
    widgets={
        "embed_html": "Embed HTML",
        "iframe": "Embed Website",
        },
    db_models=[],
    blueprints=[views.blueprint],
    index_route_url="core_extras.get_index",
    get_rendered_widget=render_widget,
    get_rendered_widget_edit=render_widget_edit,
)
