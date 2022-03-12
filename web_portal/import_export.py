import logging
from collections.abc import Generator
from typing import Iterable

from pydantic import BaseModel, constr
from tortoise.transactions import atomic

from .database.crud import cached_panels
from .database.models import Panel_Group, Panel_Widget

logger = logging.getLogger("import_export")


class Widget_V1(BaseModel):
    url: constr(max_length=255)
    prefix: constr(max_length=128)
    color_name: constr(max_length=40)
    group_prefix: constr(max_length=128)


async def export_to_v1_widgets() -> Generator[Widget_V1, None, None]:
    widgets = await Panel_Widget.all().prefetch_related("group")

    for widget in widgets:
        yield Widget_V1(
            url=widget.url,
            prefix=widget.prefix,
            color_name=widget.color_name,
            group_prefix=widget.group.prefix,
        )


@atomic()
async def import_v1_widgets(widgets: Iterable[Widget_V1]):
    for count, widget in enumerate(widgets, 1):
        logger.info("Importing widget: '%s', from v1 data", count)
        group, is_group_new = await Panel_Group.get_or_create(prefix=widget.group_prefix)
        if is_group_new:
            logger.info("Created new group during import: '%s'", group.prefix)
        await Panel_Widget.create(
            url=widget.url,
            prefix=widget.prefix,
            color_name=widget.color_name,
            group=group,
        )
        logger.info("Imported widget: '%s', from v1 data", count)
    cached_panels.reset_cache()
