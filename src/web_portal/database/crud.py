from typing import Iterator, List

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


async def new_panel_widget(url: str, prefix: str, group_id: int) -> Panel_Widget:
    widget = Panel_Widget(url=url, prefix=prefix, group_id=group_id)
    await widget.save()
    return widget


async def new_panel_group(prefix: str) -> Panel_Group:
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


async def get_widgets() -> List[Panel_Widget]:
    return await Panel_Widget.all()


async def get_widgets_by_group():
    widgets_grouped = []
    group_ids = await Panel_Group.all()
    for group in group_ids:
        widgets_grouped.append({
            "group_id": group.id,
            "group_prefix": group.prefix,
            "widgets": (await Panel_Widget.filter(group_id=group.id).all())})
    return widgets_grouped


async def get_panel_groups() -> List[Panel_Group]:
    return await Panel_Group.all()
