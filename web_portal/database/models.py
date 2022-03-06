from tortoise.fields import (BinaryField, BooleanField, CharField,
                             ForeignKeyField, ForeignKeyRelation, IntField,
                             ReverseRelation)
from tortoise.models import Model
from werkzeug.security import check_password_hash, generate_password_hash


class User(Model):
    id = IntField(pk=True)
    username = CharField(20, unique=True)
    password_hash = BinaryField()
    is_admin = BooleanField(default=False)

    def check_password(self, to_check: str) -> bool:
        return check_password_hash(self.password_hash.decode(), to_check)

    def set_password(self, new_password: str):
        self.password_hash = generate_password_hash(new_password).encode()


class Panel_Group(Model):
    id = IntField(pk=True)
    prefix = CharField(128)

    widgets = ReverseRelation["Panel_Widget"]

class Panel_Widget(Model):
    id = IntField(pk=True)
    url = CharField(255)
    prefix = CharField(128)
    color_name = CharField(40)

    group: ForeignKeyRelation[Panel_Group] = ForeignKeyField(
        "models.Panel_Group", related_name="panel_widgets"
    )
