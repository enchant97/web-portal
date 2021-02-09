from quart import Quart, render_template

app = Quart(__name__)

@app.route("/")
async def portal():
    return await render_template("portal.jinja2")

@app.route("/admin")
async def admin():
    return await render_template("admin.jinja2")
