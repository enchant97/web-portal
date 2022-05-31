from . import models, views


class Meta:
    db_models = [models]
    blueprints = [views.blueprint]
    widgets = ["links"]
