from collections.abc import Iterable
from typing import Any

from tortoise.fields import (
    BinaryField,
    BooleanField,
    CharField,
    Field,
    ForeignKeyField,
    ForeignKeyRelation,
    IntField,
    JSONField,
    ReverseRelation,
)
from tortoise.models import Model
from tortoise.transactions import atomic
from werkzeug.security import check_password_hash, generate_password_hash

from ..core.constants import PUBLIC_ACCOUNT_USERNAME


class SystemSetting(Model):
    key = CharField(128, pk=True)
    value = JSONField()


class User(Model):
    id = IntField(pk=True)  # noqa: A003
    username = CharField(128, unique=True)
    password_hash = BinaryField(null=True)
    is_admin = BooleanField(default=False)

    def check_password(self, to_check: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash.decode(), to_check)

    def set_password(self, new_password: str):
        if self.is_public_account:
            raise ValueError("Cannot set password of public account")
        self.password_hash = generate_password_hash(new_password).encode()

    @property
    def is_public_account(self):
        """
        Check whether the user is the public account
        """
        return self.username == PUBLIC_ACCOUNT_USERNAME

    @property
    def is_external_account(self):
        """
        Check whether account details
        are provided by external mechanism
        """
        return self.password_hash is None and self.username != PUBLIC_ACCOUNT_USERNAME


class Plugin(Model):
    id = IntField(pk=True)  # noqa: A003
    internal_name = CharField(128, unique=True)

    widgets = ReverseRelation["Widget"]


class Widget(Model):
    id = IntField(pk=True)  # noqa: A003
    internal_name = CharField(128, unique=True)
    plugin: ForeignKeyRelation[Plugin] = ForeignKeyField("models.Plugin", "widgets")


class Dashboard(Model):
    id = IntField(pk=True)  # noqa: A003
    owner: ForeignKeyRelation[User] = ForeignKeyField("models.User")
    widget_order: Field[list[int]] = JSONField(default=[])  # type: ignore

    widgets = ReverseRelation["DashboardWidget"]

    def widgets_sorted(self) -> Iterable["DashboardWidget"]:
        if len(self.widget_order) == 0:
            return self.widgets
        order = {v: i for i, v in enumerate(self.widget_order)}
        return sorted(self.widgets, key=lambda x: order[x.id])

    @atomic()
    async def append_widget(self, widget: "DashboardWidget"):
        await self.fetch_related("widgets")
        if len(self.widget_order) == 0:
            self.widget_order = [x.id for x in self.widgets_sorted()]
        await widget.save()
        self.widget_order.append(widget.id)
        await self.save()

    @atomic()
    async def pop_widget_by_id(self, widget_id: int):
        if len(self.widget_order) != 0:
            self.widget_order.remove(widget_id)
        await self.widgets.filter(id=widget_id).delete()
        await self.save()

    @staticmethod
    def _shift_i_left(items: list[Any], i: int):
        if i == 0:
            items.append(items.pop(i))
        else:
            left_i = i - 1
            if left_i == 0:
                items[::] = [
                    items.pop(i),
                    *items,
                ]
            else:
                items[::] = [
                    *items[:left_i],
                    items.pop(i),
                    *items[left_i:],
                ]

    async def shift_widget_left(self, widget_id: int):
        if len(self.widget_order) == 0:
            self.widget_order = [x.id for x in self.widgets_sorted()]

        current_i = self.widget_order.index(widget_id)
        if current_i == -1:
            raise KeyError(f"widget id '{widget_id}' not found")
        Dashboard._shift_i_left(self.widget_order, current_i)

        await self.save()

    async def shift_widget_right(self, widget_id: int):
        if len(self.widget_order) == 0:
            self.widget_order = [x.id for x in self.widgets_sorted()]

        current_i = self.widget_order.index(widget_id)
        if current_i == -1:
            raise KeyError(f"widget id '{widget_id}' not found")

        self.widget_order.reverse()
        current_i = self.widget_order.index(widget_id)
        Dashboard._shift_i_left(self.widget_order, current_i)
        self.widget_order.reverse()

        await self.save()


class DashboardWidget(Model):
    id = IntField(pk=True)  # noqa: A003
    name = CharField(128)
    show_header = BooleanField(default=False)
    dashboard: ForeignKeyRelation[Dashboard] = ForeignKeyField("models.Dashboard", "widgets")
    widget: ForeignKeyRelation[Widget] = ForeignKeyField("models.Widget")
    config = JSONField(null=True)
