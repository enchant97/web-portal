import pytest
from quart import Quart
from tortoise.transactions import atomic
from web_portal.database import models


class TestAdmin:
    @pytest.mark.asyncio
    async def test_get_index(self, app: Quart):
        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.get("/admin/")
            assert "Admin" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    async def test_get_widget(self, app: Quart):
        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.get("/admin/portal")
            assert "Admin" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    async def test_get_users(self, app: Quart):
        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.get("/admin/users")
            assert "Admin" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    @atomic()
    async def test_post_new_widget(self, app: Quart):
        test_url = "https://example.com"
        test_group_id = (await models.Panel_Group.first()).id
        test_prefix = "test_post_new_widget"
        test_color_name = "black"

        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.post(
                "/admin/new-widget",
                form={
                    "url": test_url,
                    "group_id": test_group_id,
                    "prefix": test_prefix,
                    "color_name": test_color_name,
                },
                follow_redirects=True,
            )
            assert "created new widget" in await response.get_data(as_text=True)

        assert await models.Panel_Widget.exists(prefix=test_prefix)

        # clean-up
        await models.Panel_Widget.filter(prefix=test_prefix).delete()

    @pytest.mark.asyncio
    @atomic()
    async def test_post_new_group(self, app: Quart):
        test_prefix = "test_post_new_group"

        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.post(
                "/admin/new-group",
                form={
                    "prefix": test_prefix,
                },
                follow_redirects=True,
            )
            assert "created new widget group" in await response.get_data(as_text=True)

        assert await models.Panel_Group.exists(prefix=test_prefix)

        # clean-up
        await models.Panel_Group.filter(prefix=test_prefix).delete()

    @pytest.mark.asyncio
    @atomic()
    async def test_post_delete_group(self, app: Quart):
        test_prefix = "test_post_delete_group"
        test_group = await models.Panel_Group.create(prefix=test_prefix)

        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.post(
                "/admin/delete-group",
                form={
                    "group_id": test_group.id,
                },
                follow_redirects=True,
            )
            assert "deleted group" in await response.get_data(as_text=True)

        assert not await models.Panel_Group.exists(id=test_group.id)

    @pytest.mark.asyncio
    @atomic()
    async def test_post_re_group_widget(self, app: Quart):
        test_prefix = "test_post_re_group_widget"

        test_group = await models.Panel_Group.create(prefix=test_prefix)
        test_group_2 = await models.Panel_Group.create(prefix=f"{test_prefix}-2")
        test_widget = await models.Panel_Widget.create(
            prefix=test_prefix, url="",
            color_name="", group=test_group,
        )

        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.post(
                "/admin/re-group-widget",
                form={
                    "widget_id": test_widget.id,
                    "group_id": test_group_2.id,
                },
                follow_redirects=True,
            )
            assert "changed widget group" in await response.get_data(as_text=True)

        await test_widget.refresh_from_db(["group_id"])
        assert test_widget.group_id == test_group_2.id

        # clean-up
        await test_group.delete()
        await test_group_2.delete()
        await test_widget.delete()


    @pytest.mark.asyncio
    @atomic()
    async def test_post_delete_widget(self, app: Quart):
        test_prefix = "test_post_delete_widget"
        test_group = await models.Panel_Group.create(prefix=test_prefix)
        test_widget = await models.Panel_Widget.create(
            prefix=test_prefix, url="",
            color_name="", group=test_group,
        )

        client = app.test_client()
        async with client.authenticated("1"):
            response = await client.post(
                "/admin/delete-widget",
                form={
                    "widget_id": test_widget.id,
                },
                follow_redirects=True,
            )
            assert "deleted widget" in await response.get_data(as_text=True)

        assert not await models.Panel_Widget.exists(id=test_widget.id)

        # clean-up
        await test_group.delete()


class TestLogin:
    @staticmethod
    def create_login_form(username: str, password: str):
        return {
            "username": username,
            "password": password,
        }

    @pytest.mark.asyncio
    async def test_get_login(self, app: Quart):
        client = app.test_client()
        response = await client.get("/auth/login")
        assert response.status_code == 200
        assert "Login" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    async def test_login_valid(self, app: Quart):
        client = app.test_client()
        response = await client.post(
            "/auth/login",
            form=self.create_login_form("admin", "admin"),
            follow_redirects=True,
        )
        assert "Log Out" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    async def test_login_invalid(self, app: Quart):
        client = app.test_client()
        response = await client.post(
            "/auth/login",
            form=self.create_login_form("admin", "wrong password 1234"),
            follow_redirects=True,
        )
        assert "username or password incorrect" in await response.get_data(as_text=True)

    @pytest.mark.asyncio
    async def test_logout(self, app: Quart):
        client = app.test_client()
        response = await client.post(
            "/auth/login",
            form=self.create_login_form("admin", "admin"),
            follow_redirects=True,
        )

        response = await client.get("/auth/logout", follow_redirects=True)
        assert "You have been logged out" in await response.get_data(as_text=True)

        response = await client.get("/auth/logout", follow_redirects=True)
        assert "You need to be logged in to view this page" in await response.get_data(as_text=True)


class TestPortal:
    @pytest.mark.asyncio
    async def test_portal(self, app: Quart):
        client = app.test_client()
        response = await client.get("/")
        assert response.status_code == 200
        assert "Portal" in await response.get_data(as_text=True)
