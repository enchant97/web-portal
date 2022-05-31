import logging

from quart import Quart, flash, redirect, url_for
from quart_auth import AuthManager, Unauthorized
from tortoise.contrib.quart import register_tortoise
from web_health_checker.contrib import quart as health_check

from . import __version__
from .config import get_settings
from .database import models
from .database.crud import create_default_admin, create_default_panel_group
from .views import login, portal

# HACK
from .plugins.web_links.views import blueprint as web_links_blueprint
from .plugins.web_links import models as web_links_models

app = Quart(__name__)
auth_manager = AuthManager()


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "red")
    return redirect(url_for("login.login"))


@app.before_first_request
async def first_request():
    await create_default_admin(get_settings().ADMIN_CREATE_OVERRIDE)
    await create_default_panel_group()

    # HACK
    plugin, created = await models.Plugin.update_or_create(internal_name="web_links")
    if created:
        await models.Widget.update_or_create(internal_name="web_links__links", defaults={
            "plugin":plugin
        })


def create_app():
    logging.basicConfig(
        level=logging.getLevelName(get_settings().LOG_LEVEL))
    logging.debug("loading config")
    # do config
    app.config["__VERSION__"] = __version__
    app.secret_key = get_settings().SECRET_KEY
    app.config["QUART_AUTH_COOKIE_SECURE"] = not get_settings().UNSECURE_LOGIN
    app.config["SEARCH_URL"] = get_settings().SEARCH_URL
    app.config["SHOW_PANEL_HEADERS"] = get_settings().SHOW_PANEL_HEADERS
    app.config["COMPACT_VIEW"] = get_settings().COMPACT_VIEW
    app.config["OPEN_TO_NEW_TAB"] = get_settings().OPEN_TO_NEW_TAB
    logging.debug("registering blueprints")
    # register blueprints
    app.register_blueprint(health_check.blueprint, url_prefix="/")
    app.register_blueprint(portal.blueprint, url_prefix="/")
    app.register_blueprint(login.blueprint, url_prefix="/auth")

    # HACK
    app.register_blueprint(web_links_blueprint, url_prefix="/plugins/web_links")

    logging.debug("registering tortoise-orm")
    # other setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules={
            "models": [models],
            # HACK
            "web_links": [web_links_models]},
        generate_schemas=True)
    logging.debug("init auth manager")
    auth_manager.init_app(app)
    logging.debug("created app")

    return app
