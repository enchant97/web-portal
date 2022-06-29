import logging
from typing import Iterable

from pydantic import BaseModel, constr
from tortoise.exceptions import IntegrityError
from tortoise.transactions import atomic

from .core.plugin import PluginHandler

logger = logging.getLogger("import_export")


class Widget_V1(BaseModel):
    url: constr(max_length=255)
    prefix: constr(max_length=128)
    color_name: constr(max_length=40)
    group_prefix: constr(max_length=128)


@atomic()
async def import_v1_widgets(widgets: Iterable[Widget_V1]) -> int:
    try:
        core_plugin = PluginHandler.get_loaded_plugin("core")
    except KeyError:
        logger.error("Cannot import v1 widgets due to plugin missing")
        return -1

    count = 0

    for count, widget in enumerate(widgets, 1):
        logger.info("Importing widget: '%s', from v1 data", count)
        try:
            # NOTE this directly uses the plugin's models
            await core_plugin.meta.db_models[0].Link.create(
                name=widget.prefix,
                url=widget.url,
                color_name=widget.color_name,
            )
        except IntegrityError:
            logger.info("Skipped widget: '%s' prefix already exists", widget.prefix)
        else:
            logger.info("Imported widget: '%s', from v1 data", count)

    return count
