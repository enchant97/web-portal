import logging

from quart import Quart, flash, redirect, request, url_for
from quart_auth import AuthManager, Unauthorized
from tortoise.contrib.quart import register_tortoise

from . import __version__
from .config import get_settings
from .database import models
from .database.crud import create_default_admin, create_default_panel_group
from .views import admin, login, portal

BASE_URL = get_settings().BASE_URL
if BASE_URL == "/":
    BASE_URL = ""

app = Quart(__name__, static_url_path=BASE_URL + "/static")
auth_manager=AuthManager()

@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "red")
    return redirect(url_for("login.login"))

if BASE_URL != "":
    # allow redirect to index if base url was set
    @app.route("/")
    async def redirect_to_portal():
        logging.info("redirecting / to %s, as BASE_URL was set", BASE_URL)
        return redirect(url_for('portal.portal'))

@app.before_first_request
async def first_request():
    await create_default_admin(get_settings().ADMIN_CREATE_OVERRIDE)
    await create_default_panel_group()

def create_app():
    logging.basicConfig(
        level=logging.getLevelName(get_settings().LOG_LEVEL))
    logging.debug("loading config")
    # do config
    app.config["__VERSION__"] = __version__
    app.secret_key = get_settings().SECRET_KEY
    app.config["QUART_AUTH_COOKIE_SECURE"] = not get_settings().UNSECURE_LOGIN
    logging.debug("registering blueprints")
    # register blueprints
    app.register_blueprint(portal.blueprint, url_prefix=BASE_URL+"/")
    app.register_blueprint(login.blueprint, url_prefix=BASE_URL+"/auth")
    app.register_blueprint(admin.blueprint, url_prefix=BASE_URL+"/admin")
    logging.debug("registering tortoise-orm")
    # other setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URL,
        modules={"models": [models]},
        generate_schemas=True)
    logging.debug("init auth manager")
    auth_manager.init_app(app)
    logging.debug("created app")
    return app
