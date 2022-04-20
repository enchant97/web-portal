import asyncio

import pytest
import pytest_asyncio
from quart.app import Quart
from tortoise import Tortoise
from web_portal.config import Settings, get_settings
from web_portal.database import models
from web_portal.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app_config() -> Settings:
    return get_settings()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_tests(app_config):
    await Tortoise.init(
        db_url=app_config.DB_URI,
        modules={"models": [models]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise._drop_databases()


@pytest.fixture(scope="session")
def app() -> Quart:
    return create_app()
