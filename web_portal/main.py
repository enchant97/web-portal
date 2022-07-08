import logging

from quart import Quart, flash, redirect, url_for
from quart_auth import AuthManager
from tortoise.contrib.quart import register_tortoise
from web_health_checker.contrib import quart as health_check

from . import __version__
from .core.auth import AuthUserEnhanced
from .core.config import get_settings
from .core.plugin import PluginHandler, make_combined_widget_name
from .database import models
from .views import admin, install, login, portal, settings

logger = logging.getLogger("web-portal")

app = Quart(__name__)
auth_manager = AuthManager()
auth_manager.user_class = AuthUserEnhanced


@app.errorhandler(401)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "red")
    return redirect(url_for("login.get_login"))


@app.before_first_request
async def first_request():
    # NOTE this ensures plugins and widgets are registed in database
    for plugin in PluginHandler.loaded_plugins().values():
        plugin_model, _ = await models.Plugin.update_or_create(internal_name=plugin.internal_name)

        for widget_name in plugin.meta.widgets:
            name = make_combined_widget_name(plugin.internal_name, widget_name)
            await models.Widget.update_or_create(internal_name=name, defaults={
                "plugin": plugin_model
            })


@app.context_processor
def context_get_head_injects():
    # TODO store rendered output in variable instead at app launch (performance improvement)
    async def get_head_injects():
        for plugin in PluginHandler.get_loaded_plugin_values():
            if plugin.meta.get_injected_head:
                yield await plugin.meta.get_injected_head()
    return dict(get_head_injects=get_head_injects)


def create_app():
    logging.basicConfig()
    logger.setLevel(logging.getLevelName(get_settings().LOG_LEVEL))

    logger.debug("loading config")
    # do config
    app.config["__VERSION__"] = __version__
    app.secret_key = get_settings().SECRET_KEY
    app.config["QUART_AUTH_COOKIE_SECURE"] = not get_settings().UNSECURE_LOGIN
    logger.debug("registering blueprints")
    # register blueprints
    app.register_blueprint(health_check.blueprint, url_prefix="/")
    app.register_blueprint(portal.blueprint, url_prefix="/")
    app.register_blueprint(login.blueprint, url_prefix="/auth")
    app.register_blueprint(settings.blueprint, url_prefix="/settings")
    app.register_blueprint(admin.blueprint, url_prefix="/admin")
    app.register_blueprint(install.blueprint, url_prefix="/install")

    db_models = {"models": [models]}

    logger.debug("loading plugins")
    for plugin in PluginHandler.load_plugins(__version__):
        # register plugin settings
        if plugin.meta.get_settings:
            app.config[f"plugin__{plugin.internal_name}"] = plugin.meta.get_settings()
        # register quart blueprints
        for blueprint in plugin.meta.blueprints:
            url_prefix = f"/plugins/{plugin.internal_name}"
            if blueprint.url_prefix:
                url_prefix += blueprint.url_prefix
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        # register database models
        if plugin.meta.db_models:
            db_models[plugin.internal_name] = plugin.meta.db_models

    logger.debug("registering tortoise-orm")
    # other setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules=db_models,
        generate_schemas=True)
    logger.debug("init auth manager")
    auth_manager.init_app(app)
    logger.debug("created app")

    return app
