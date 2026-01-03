from quart import Blueprint, abort, redirect, url_for
from quart_auth import login_user

from web_portal.core.auth import AuthUserEnhanced
from web_portal.core.config import get_settings
from web_portal.database import models

blueprint = Blueprint("e2e_testing", __name__, url_prefix="/_e2e")


@blueprint.before_request
def require_e2e_enabled():
    if not get_settings().ENABLE_E2E_TESTING_API:
        abort(404)


@blueprint.get("/login_as_user/<username>")
async def login_as_user(username: str):
    user = await models.User.filter(username=username).get_or_none()
    if user:
        login_user(AuthUserEnhanced(str(user.id)))
        return redirect(url_for("portal.portal"))
    abort(500)
    return
