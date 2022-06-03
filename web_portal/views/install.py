from quart import Blueprint, render_template

from ..database import models
from ..helpers import ensure_not_setup

blueprint = Blueprint("install", __name__)



@blueprint.get("/")
@ensure_not_setup
async def get_index():
    return await render_template("install/index.jinja")
