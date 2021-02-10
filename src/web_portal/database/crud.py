from typing import List

from tortoise.exceptions import DoesNotExist

from .models import Panel_Group, Panel_Widget, User


async def create_default_admin(override=False):
    """
    create a default admin account

    :param override: create a new admin
                     even if one already
                     exists, defaults to False
    """
    if override:
        raise NotImplementedError("this has not been implemented yet")

    if not await User.filter(username="admin").first():
        account = User(username="admin", is_admin=True)
        account.set_password("admin")
        await account.save()


async def create_default_panel_group():
    """
    creates the default panel group if none exist
    """
    if not await Panel_Group.first():
        default_group = Panel_Group(prefix="default")
        await default_group.save()


async def new_user(username: str, password: str, is_admin: bool) -> User:
    """
    create a new user

        :param username: the username
        :param password: the password
        :param is_admin: whether they are a admin
        :return: the created User row
    """
    user = User(username=username, is_admin=is_admin)
    user.set_password(password)
    await user.save()
    return user


async def new_panel_widget(
    url: str,
    prefix: str,
    color_name: str,
    group_id: int) -> Panel_Widget:
    """
    create a new widget

        :param url: the url
        :param prefix: the prefix
        :param color_name: the background color
        :param group_id: the group id it belongs to
        :return: the created row
    """
    widget = Panel_Widget(
        url=url,
        prefix=prefix,
        color_name=color_name,
        group_id=group_id)
    await widget.save()
    return widget


async def new_panel_group(prefix: str) -> Panel_Group:
    """
    create a new panel group

        :param prefix: the prefix
        :return: the created row
    """
    group = Panel_Group(prefix=prefix)
    await group.save()
    return group


async def check_user(username: str, password: str) -> User:
    """
    used to validate whether the user details are valid

        :param username: username to check
        :param password: password to check
        :return: the User or None
    """
    user = await User.filter(username=username).first()
    if user:
        if user.check_password(password):
            return user
    return None


async def check_is_admin(user_id: int) -> bool:
    """
    check whether a user has admin,
    will return False if no user exists

        :param user_id: the user id to check
        :return: whether user is admin
    """
    user = await User.filter(id=user_id).first()
    if user is None:
        return False
    return user.is_admin


async def get_users() -> List[User]:
    """
    get all users in database

        :return: each user row in a list
    """
    return await User.all()


async def get_widgets() -> List[Panel_Widget]:
    """
    get all widgets

        :return: all the widgets
    """
    return await Panel_Widget.all()


async def get_widgets_by_group():
    """
    get all widgets by their group

        :return: the grouped widgets as list
    """
    widgets_grouped = []
    group_ids = await Panel_Group.all()
    for group in group_ids:
        widgets_grouped.append({
            "group_id": group.id,
            "group_prefix": group.prefix,
            "widgets": (await Panel_Widget.filter(group_id=group.id).all())})
    return widgets_grouped


async def get_panel_groups() -> List[Panel_Group]:
    """
    get all groups

        :return: the group rows as list
    """
    return await Panel_Group.all()


async def modify_user_permissions(user_id: int, is_admin: bool):
    """
    modify a users's permissions

        :param user_id: the user's id
        :param is_admin: whether they are a admin
    """
    await User.filter(id=user_id).update(is_admin=is_admin)


async def modify_user_password(user_id: int, new_password: str):
    """
    change a user's password

        :param user_id: the user's id
        :param new_password: the new password
    """
    user = await User.filter(id=user_id).first()
    if not user:
        raise DoesNotExist("user id does not exist")
    user.set_password(new_password)
    await user.save()


async def modify_widget_group(widget_id: int, group_id: int):
    """
    modify a widget's group

        :param widget_id: the widget id
        :param group_id: the group id
    """
    await Panel_Widget.filter(id=widget_id).update(group_id=group_id)


async def modify_widget_color(widget_id: int, color_name: str):
    """
    modify a widget's color

        :param widget_id: the widget id
        :param color_name: the color
    """
    await Panel_Widget.filter(id=widget_id).update(color_name=color_name)


async def delete_user(user_id: int):
    """
    delete a user

        :param user_id: the user's id
    """
    await User.filter(id=user_id).delete()


async def delete_widget_by_id(widget_id: int):
    """
    delete a widget by it's id

        :param widget_id: the widget id
    """
    await Panel_Widget.filter(id=widget_id).delete()
