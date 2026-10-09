import pytest
import pytest_asyncio
from quart import Quart
from tortoise import Tortoise

from web_portal import plugin_api
from web_portal.database.models import SystemSetting


@pytest_asyncio.fixture(autouse=True, loop_scope="function")
async def settings_context():
    app = Quart(__name__)
    async with app.app_context():
        await Tortoise.init(
            db_url="sqlite://:memory:", modules={"models": ["web_portal.database.models"]}
        )
        try:
            await Tortoise.generate_schemas()
            yield
        finally:
            await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_missing_plugin_setting_returns_default():
    assert await plugin_api.get_plugin_system_setting("example", "missing") is None
    assert (
        await plugin_api.get_plugin_system_setting("example", "missing", default="fallback")
        == "fallback"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [{"enabled": True}, False, 0])
async def test_plugin_setting_round_trip(value):
    other_value = {"name": "other"}
    await plugin_api.set_plugin_system_setting("example", "option", value)
    await plugin_api.set_plugin_system_setting("other", "option", other_value)

    assert await plugin_api.get_plugin_system_setting("example", "option") == value
    # A separate app context has no cached values, so these reads use SQLite.
    async with Quart("uncached").app_context():
        assert await plugin_api.get_plugin_system_setting("example", "option") == value
        assert await plugin_api.get_plugin_system_setting("other", "option") == other_value

    await plugin_api.remove_plugin_system_setting("example", "option")
    assert await plugin_api.get_plugin_system_setting("example", "option") is None
    assert await plugin_api.get_plugin_system_setting("other", "option") == other_value


@pytest.mark.asyncio
async def test_plugin_setting_can_bypass_cache():
    cached = {"state": "cached"}
    updated = {"state": "updated"}
    await plugin_api.set_plugin_system_setting("example", "option", cached)
    await SystemSetting.filter(key="plugin__example_option").update(value=updated)

    assert await plugin_api.get_plugin_system_setting("example", "option") == cached
    assert (
        await plugin_api.get_plugin_system_setting("example", "option", skip_cache=True) == updated
    )
    assert await plugin_api.get_plugin_system_setting("example", "option") == updated
