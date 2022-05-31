from . import models, views


class Meta:
    human_name = "web links"
    db_models = [models]
    blueprints = [views.blueprint]
    widgets = {"links": "links"}
