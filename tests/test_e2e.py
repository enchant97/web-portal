import time
from subprocess import Popen
import shutil

import pytest
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    hatch_bin = shutil.which("hatch")
    if hatch_bin is None:
        raise Exception("could not locate 'hatch' executable")
    proc = Popen(
        [hatch_bin, "run", "serve"],
        env={
            "DB_URI": "sqlite://:memory:",
            "SECRET_KEY": "testing_e2e",
            "UNATTENDED_DEMO_INSTALL": "1",
            "PLUGINS_PATH": "./plugins",
            "DATA_PATH": "./data",
        },
    )
    time.sleep(5)  # XXX Find a better way
    try:
        page.goto(BASE_URL)
        yield
    finally:
        proc.terminate()


def test_login(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.locator("#username").fill("demo")
    page.locator("#password").fill("demo")
    page.locator("button[type=submit]").click()
    page.wait_for_url(BASE_URL)
