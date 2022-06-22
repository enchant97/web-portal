from pathlib import Path
from shutil import copytree
from web_portal.plugin_api import get_plugin_data_path

ICONS_PATH = get_plugin_data_path("core") / "icons"


def get_icon_names() -> set[str]:
    """
    Gets all icon names found in the icons folder

        :return: icon names
    """
    names = set(path.stem for path in ICONS_PATH.glob("**/*"))
    return names


def get_icon_path(icon_name: str) -> Path | None:
    """
    Gets the icons image path,
    returning None if none were found

        :param icon_name: The icon's name
        :return: The file path or None
    """
    search_paths = [
        # NOTE ensure svg is at first index for priority
        ICONS_PATH / f"svg/{icon_name}.svg",
        ICONS_PATH / f"png/{icon_name}.png",
    ]

    for path in search_paths:
        if path.is_file():
            return path


def copy_icons_from_import(src: Path):
    copytree(Path(src, "png"), ICONS_PATH / "png", dirs_exist_ok=True)
    copytree(Path(src, "svg"), ICONS_PATH / "svg", dirs_exist_ok=True)
