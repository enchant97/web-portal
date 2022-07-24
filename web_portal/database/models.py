from tortoise.fields import (BinaryField, BooleanField, CharField,
                             ForeignKeyField, ForeignKeyRelation, IntField,
                             JSONField, ReverseRelation)
from tortoise.models import Model
from werkzeug.security import check_password_hash, generate_password_hash

from ..core.constants import PUBLIC_ACCOUNT_USERNAME


class SystemSetting(Model):
    key = CharField(128, pk=True)
    value = JSONField()


class User(Model):
    id = IntField(pk=True)
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
    id = IntField(pk=True)
    internal_name = CharField(128, unique=True)

    widgets = ReverseRelation["Widget"]


class Widget(Model):
    id = IntField(pk=True)
    internal_name = CharField(128, unique=True)
    plugin: ForeignKeyRelation[Plugin] = ForeignKeyField("models.Plugin", "widgets")


class Dashboard(Model):
    id = IntField(pk=True)
    owner: ForeignKeyRelation[User] = ForeignKeyField("models.User")

    widgets = ReverseRelation["DashboardWidget"]


class DashboardWidget(Model):
    id = IntField(pk=True)
    name = CharField(128)
    dashboard: ForeignKeyRelation[Dashboard] = ForeignKeyField("models.Dashboard", "widgets")
    widget: ForeignKeyRelation[Widget] = ForeignKeyField("models.Widget")
    config = JSONField(null=True)
