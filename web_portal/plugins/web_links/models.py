from tortoise.fields import CharField, IntField, TextField
from tortoise.models import Model


class Link(Model):
    id = IntField(pk=True)
    name = CharField(128, unique=True)
    url = TextField()
    color_name = CharField(128)

    class Meta:
        table = "web_links__link"
