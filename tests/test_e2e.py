import time
from subprocess import Popen

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    proc = Popen(
        ["hatch", "run", "serve"],
        env={
            "DB_URI": "sqlite://:memory:",
            "SECRET_KEY": "testing_e2e",
            "UNATTENDED_DEMO_INSTALL": "1",
        },
    )
    time.sleep(5)  # XXX Find a better way
    try:
        page.goto("http://127.0.0.1:8000")
        yield
    finally:
        proc.terminate()


def test_login(page: Page):
    page.goto("/auth/login")
    page.locator("#username").fill("demo")
    page.locator("#password").fill("demo")
    page.locator("button[type=submit]").click()
    page.wait_for_url("/")
