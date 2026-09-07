import os
import shutil
import signal
import time
import typing
from http import HTTPStatus
from subprocess import Popen
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect

if typing.TYPE_CHECKING:
    from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8000"


def _wait_for_ready(*, timeout=15, interval=0.5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(f"{BASE_URL}/is-healthy", timeout=2) as resp:
                if resp.status == HTTPStatus.OK:
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
        preexec_fn=os.setsid,  # noqa: PLW1509
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


def test_logout(page: Page):
    page.goto(f"{BASE_URL}/_e2e/login_as_user/demo")
    page.get_by_test_id("logout_aelc").click()
    page.wait_for_url(f"{BASE_URL}/auth/login")


def test_change_password(page: Page):
    page.goto(f"{BASE_URL}/_e2e/login_as_user/demo")
    page.get_by_test_id("settings_drjr").click()
    page.wait_for_url(f"{BASE_URL}/settings/")
    page.get_by_test_id("myaccount_pjjx").click()
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


def test_admin_adjust_public_portal(page: Page):
    def do_adjustment(*, enable_public: bool):
        page.goto(f"{BASE_URL}/_e2e/login_as_user/admin")
        page.get_by_test_id("settings_drjr").click()
        page.wait_for_url(f"{BASE_URL}/settings/")
        page.get_by_test_id("admin_zeec").click()
        page.wait_for_url(f"{BASE_URL}/admin/")
        page.get_by_test_id("settings_ljbz").click()
        page.wait_for_url(f"{BASE_URL}/admin/system-settings/")
        page.locator("#system-setting-public-portal").set_checked(enable_public)
        page.get_by_test_id("submit_qoyc").click()
        page.wait_for_url(f"{BASE_URL}/admin/system-settings/")
        page.context.clear_cookies()
        page.goto(f"{BASE_URL}")

    do_adjustment(enable_public=True)
    expect(page.locator("body header h1")).to_have_text("Portal")
    do_adjustment(enable_public=False)
    page.wait_for_url(f"{BASE_URL}/auth/login")


def test_admin_change_branding(page: Page):
    page.goto(f"{BASE_URL}/_e2e/login_as_user/admin")
    page.get_by_test_id("settings_drjr").click()
    page.wait_for_url(f"{BASE_URL}/settings/")
    page.get_by_test_id("admin_zeec").click()
    page.wait_for_url(f"{BASE_URL}/admin/")
    page.get_by_test_id("settings_ljbz").click()
    page.wait_for_url(f"{BASE_URL}/admin/system-settings/")
    new_brand_title = "My Dashboard"
    page.locator("#branding-title").fill(new_brand_title)
    page.get_by_test_id("submit_agjw").click()
    page.wait_for_url(f"{BASE_URL}/admin/system-settings/")
    page.goto(f"{BASE_URL}")
    expect(page.locator("body header h1")).to_have_text(new_brand_title)


def test_edit_link_preserves_color_and_icon(page: Page):
    page.goto(f"{BASE_URL}/_e2e/login_as_user/admin")
    page.goto(f"{BASE_URL}/plugins/core/links")

    link_row = page.locator("tbody tr").filter(has_text="Bitwarden")
    link_row.get_by_title("Edit").click()

    expect(page.locator("#core-link-color-name")).to_have_value("cyan")
    expect(page.locator("#core-link-icon-name")).to_have_value("bitwarden")

    page.locator("#core-link-name").fill("Bitwarden Vault")
    page.locator("button[type=submit]").click()
    page.wait_for_url(f"{BASE_URL}/plugins/core/links")

    edited_row = page.locator("tbody tr").filter(has_text="Bitwarden Vault")
    edited_row.get_by_title("Edit").click()
    expect(page.locator("#core-link-color-name")).to_have_value("cyan")
    expect(page.locator("#core-link-icon-name")).to_have_value("bitwarden")
