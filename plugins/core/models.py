from enum import Enum

from tortoise.fields import CharEnumField, CharField, IntField, TextField
from tortoise.models import Model


class SearchEngineMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class Link(Model):
    id = IntField(pk=True)
    name = CharField(128, unique=True)
    url = TextField()
    color_name = CharField(128)
    icon_name = CharField(128, null=True)

    class Meta:
        table = "core__link"


class SearchEngine(Model):
    id = IntField(pk=True)
    name = CharField(128, unique=True)
    url = TextField()
    query_param = CharField(128)
    method = CharEnumField(SearchEngineMethod)

    class Meta:
        table = "core__searchengine"
