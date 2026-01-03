import time
from subprocess import Popen
import shutil

import pytest
from playwright.sync_api import Page
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

BASE_URL = "http://127.0.0.1:8000"


def _wait_for_ready(*, timeout=15, interval=0.5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(f"{BASE_URL}/is-healthy", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (URLError, HTTPError):
            pass
        time.sleep(interval)
    raise TimeoutError("timed out before in ready state")


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
            "ENABLE_E2E_TESTING_API": "1",
            "PLUGINS_PATH": "./plugins",
            "DATA_PATH": "./data",
        },
    )
    try:
        _wait_for_ready()
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
