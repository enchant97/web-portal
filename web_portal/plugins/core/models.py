from tortoise.fields import CharField, IntField, TextField
from tortoise.models import Model


class Link(Model):
    id = IntField(pk=True)
    name = CharField(128, unique=True)
    url = TextField()
    color_name = CharField(128)
    icon_name = CharField(128, null=True)

    class Meta:
        table = "core__link"
