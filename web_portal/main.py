import logging

from quart import Quart, flash, redirect, url_for
from quart_auth import AuthManager
from tortoise.contrib.quart import register_tortoise
from web_health_checker.contrib import quart as health_check
from werkzeug.security import generate_password_hash

from . import __version__
from .config import get_settings
from .database import models
from .helpers import PluginHandler, make_combined_widget_name
from .views import login, portal

app = Quart(__name__)
auth_manager = AuthManager()


@app.errorhandler(401)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "red")
    return redirect(url_for("login.login"))


@app.before_first_request
async def first_request():
    # TODO move into app setup wizard will provide this instead
    await models.User.get_or_create(username="admin", defaults={
        "password_hash": generate_password_hash("admin").encode(),
        "is_admin": True,
    })
    await models.User.get_or_create(username="guest", defaults={
        "password_hash": generate_password_hash("guest").encode(),
    })

    # NOTE this ensures plugins and widgets are registed in database
    for plugin in PluginHandler.loaded_plugins().values():
        plugin_model, _ = await models.Plugin.update_or_create(internal_name=plugin.internal_name)

        for widget_name in plugin.widgets:
            name = make_combined_widget_name(plugin.internal_name, widget_name)
            await models.Widget.update_or_create(internal_name=name, defaults={
                "plugin":plugin_model
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

    db_models = {"models": [models]}

    logging.debug("loading plugins")
    for plugin in PluginHandler.load_plugins():
        for blueprint in plugin.blueprints:
            url_prefix = f"/plugins/{plugin.internal_name}"
            if blueprint.url_prefix:
                url_prefix += blueprint.url_prefix
            app.register_blueprint(blueprint, url_prefix=url_prefix)

        if plugin.db_models:
            db_models[plugin.internal_name] = plugin.db_models

    logging.debug("registering tortoise-orm")
        # other setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules=db_models,
        generate_schemas=True)
    logging.debug("init auth manager")
    auth_manager.init_app(app)
    logging.debug("created app")

    return app
