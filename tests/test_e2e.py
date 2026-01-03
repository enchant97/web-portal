import os
import shutil
import signal
import time
from subprocess import Popen
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page

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
        preexec_fn=os.setsid,
    )
    try:
        _wait_for_ready()
        page.goto(BASE_URL)
        yield
    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait()

def test_login(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.locator("#username").fill("demo")
    page.locator("#password").fill("demo")
    page.locator("button[type=submit]").click()
    page.wait_for_url(BASE_URL)


def test_change_password(page: Page):
    page.goto(f"{BASE_URL}/_e2e/login_as_user/demo")
    page.get_by_title("Settings").click()
    page.wait_for_url(f"{BASE_URL}/settings/")
    page.get_by_text("My Account").click()
    page.wait_for_url(f"{BASE_URL}/settings/account")
    page.locator("#current-password").fill("demo")
    page.locator("#new-password").fill("akgGG308")
    page.locator("#confirm-new-password").fill("akgGG308")
    page.locator("button[type=submit]").click()
    page.wait_for_url(f"{BASE_URL}/auth/login")
    page.locator("#username").fill("demo")
    page.locator("#password").fill("akgGG308")
    page.locator("button[type=submit]").click()
    page.wait_for_url(BASE_URL)
