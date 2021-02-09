import asyncio

import quart.flask_patch
from flask_login import LoginManager, login_required, login_user, logout_user
from quart import Quart, redirect, render_template, request, url_for
from tortoise.contrib.quart import register_tortoise

from .config import get_settings
from .database import models
from .database.crud import (check_user, create_default_admin,
                            create_default_panel_group, get_panel_groups,
                            get_widgets, new_panel_widget)
from .database.models import User

app = Quart(__name__)
register_tortoise(
    app,
    db_url=get_settings().DB_URL,
    modules={"models": [models]},
    generate_schemas=True)
app.secret_key = get_settings().SECRET_KEY
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    # monkey patch asyncio event loop
    return asyncio.get_event_loop().sync_wait(User.filter(id=user_id).first())

@app.route("/")
async def portal():
    widgets = await get_widgets()
    return await render_template("portal.jinja2", widgets=widgets)

@app.route("/admin")
@login_required
async def admin():
    groups = await get_panel_groups()
    return await render_template("admin.jinja2", groups=groups)

@app.route("/admin/new-widget", methods=["POST"])
@login_required
async def new_widget():
    url = (await request.form)["url"]
    group_id = (await request.form)["group_id"]
    prefix = (await request.form)["prefix"]
    await new_panel_widget(url, prefix, group_id)
    return redirect(url_for("admin"))

@app.route("/login", methods=['GET', 'POST'])
async def login():
    if request.method == "POST":
        username = (await request.form)['username']
        password = (await request.form).get('password', '')
        user = await check_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for("portal"))

    return await render_template("login.jinja2")

@app.route("/logout")
@login_required
async def logout():
    logout_user()
    return redirect(url_for("portal"))

@app.before_first_request
async def first_request():
    await create_default_admin(get_settings().ADMIN_CREATE_OVERRIDE)
    await create_default_panel_group()
