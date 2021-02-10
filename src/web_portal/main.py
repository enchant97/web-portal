import logging

from quart import Quart, flash, redirect, render_template, request, url_for
from quart_auth import AuthManager, Unauthorized, current_user
from tortoise.contrib.quart import register_tortoise

from .config import get_settings
from .database import models
from .database.crud import (check_user, create_default_admin,
                            create_default_panel_group, get_widgets_by_group)
from .views import admin, login

app = Quart(__name__)
auth_manager=AuthManager()

@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    await flash("You need to be logged in to view this page", "red")
    return redirect(url_for("login.login"))

@app.route("/")
async def portal():
    if get_settings().PORTAL_SECURED:
        # if the user has made the portal login protected
        if not (await current_user.is_authenticated):
            await flash("You need to be logged in to view this page", "red")
            return redirect(url_for("login.login"))
    widgets = await get_widgets_by_group()
    return await render_template(
        "portal.jinja2",
        widgets_grouped=widgets,
        show_panel_headers=get_settings().SHOW_PANEL_HEADERS)

@app.route("/is-alive")
async def is_alive():
    # route to test whether server has not crashed
    return "🆗"

@app.before_first_request
async def first_request():
    await create_default_admin(get_settings().ADMIN_CREATE_OVERRIDE)
    await create_default_panel_group()

def create_app():
    logging.basicConfig(
        level=logging.getLevelName(get_settings().LOG_LEVEL))
    logging.debug("loading config")
    # do config
    app.secret_key = get_settings().SECRET_KEY
    app.config["QUART_AUTH_COOKIE_SECURE"] = not get_settings().UNSECURE_LOGIN
    logging.debug("registering blueprints")
    # register blueprints
    app.register_blueprint(admin.blueprint)
    app.register_blueprint(login.blueprint)
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
