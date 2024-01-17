import logging
from importlib import import_module
from pathlib import Path
from secrets import token_urlsafe

from quart import Quart, flash, redirect, url_for
from quart_auth import QuartAuth
from tortoise.contrib.quart import register_tortoise
from web_health_checker.contrib import quart as health_check

from . import __version__
from .core.auth import AuthUserEnhanced
from .core.config import get_settings
from .core.constants import PUBLIC_ACCOUNT_USERNAME
from .core.demo import do_demo_install
from .core.helpers import get_system_setting
from .core.plugin import PluginHandler, make_combined_widget_name
from .database import models

logger = logging.getLogger("web-portal")

app = Quart(__name__)
auth_manager = QuartAuth()
auth_manager.user_class = AuthUserEnhanced


@app.errorhandler(401)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "error")
    return redirect(url_for("login.get_login"))


async def setup_internals():
    # NOTE this ensures public virtual account is always created
    await models.User.update_or_create(
        defaults={"password_hash": None},
        username=PUBLIC_ACCOUNT_USERNAME
    )

    # NOTE this ensures plugins and widgets are registed in database
    for plugin in PluginHandler.loaded_plugins().values():
        plugin_model, _ = await models.Plugin.update_or_create(internal_name=plugin.internal_name)

        for widget_name in plugin.meta.widgets:
            name = make_combined_widget_name(plugin.internal_name, widget_name)
            await models.Widget.update_or_create(internal_name=name, defaults={
                "plugin": plugin_model
            })

    if get_settings().UNATTENDED_DEMO_INSTALL:
        logger.info("unattended install of demo running")
        await do_demo_install()

    # HACK Quart's config needs to have db loading added
    await get_system_setting("DEMO_MODE")


@app.context_processor
def context_get_head_injects():
    # TODO store rendered output in variable instead at app launch (performance improvement)
    async def get_head_injects():
        for plugin in PluginHandler.get_loaded_plugin_values():
            if plugin.meta.get_injected_head:
                yield await plugin.meta.get_injected_head()
    return dict(get_head_injects=get_head_injects)


def load_plugins(app: Quart) -> dict:
    db_models = {}
    for plugin in PluginHandler.load_plugins(__version__, get_settings().PLUGIN_SKIP_LIST):
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
    return db_models


def register_blueprints(app: Quart):
    app.register_blueprint(health_check.blueprint, url_prefix="/")

    root = Path(__file__).parent / "views"

    for path in root.glob("*"):
        if (name := path.stem) != "__init__" and path.is_file():
            view = import_module("." + name, "web_portal.views")
            app.register_blueprint(view.blueprint)


def setup_configs(app: Quart):
    logging.basicConfig()
    logger.setLevel(logging.getLevelName(get_settings().LOG_LEVEL))

    app.config["__VERSION__"] = __version__
    if get_settings().SECRET_KEY:
        app.secret_key = get_settings().SECRET_KEY
    else:
        logger.warning("SECRET_KEY not set, generating random key")
        app.secret_key = token_urlsafe(128)
    app.config["QUART_AUTH_COOKIE_NAME"] = "WEB-PORTAL-AUTH"
    app.config["QUART_AUTH_COOKIE_SECURE"] = get_settings().SECURE_COOKIES
    app.config["PUBLIC_ACCOUNT_USERNAME"] = PUBLIC_ACCOUNT_USERNAME
    app.config["SHOW_VERSION_NUMBER"] = get_settings().SHOW_VERSION_NUMBER


def create_app():
    logger.debug("loading config")
    setup_configs(app)

    logger.debug("registering blueprints")
    register_blueprints(app)

    db_models = {"models": [models]}

    if not get_settings().DISABLE_PLUGIN_LOADER:
        logger.debug("loading plugins")
        plugin_models = load_plugins(app)
        db_models.update(plugin_models)
    else:
        logger.warning("plugin loading has been disabled by app config")

    logger.debug("registering tortoise-orm")
    # NOTE must be setup before any other hooks
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules=db_models,
        generate_schemas=True)

    app.before_serving(setup_internals)

    auth_manager.init_app(app)

    logger.debug("created app")

    return app
