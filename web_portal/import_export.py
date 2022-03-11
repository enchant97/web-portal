from collections.abc import Generator
from pydantic import BaseModel, constr
from .database.models import Panel_Widget


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
