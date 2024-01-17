from functools import lru_cache
from pathlib import Path
from shutil import copytree
from typing import NamedTuple, Optional
from zipfile import ZipFile

from pydantic_settings import BaseSettings

from web_portal.plugin_api import get_plugin_data_path

ICONS_PATH = get_plugin_data_path("core") / "icons"
VALID_UPLOAD_EXTENSIONS = (
    ".zip",
)


class PluginSettings(BaseSettings):
    ALLOW_ICON_UPLOADS: Optional[bool] = True
    OPEN_TO_NEW_TAB: Optional[bool] = True


@lru_cache
def get_settings():
    return PluginSettings()


class IconsImportStats(NamedTuple):
    png_count: int
    svg_count: int


def get_icon_names(sort: bool = False) -> set[str]:
    """
    Gets all icon names found in the icons folder

        :param sort: Sort the icon names into order
        :return: Icon names
    """
    names = set(path.stem for path in ICONS_PATH.glob("**/*"))
    if sort:
        names = sorted(names)
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


def copy_icons_from_import(src: Path) -> IconsImportStats:
    png_count = 0
    svg_count = 0

    if (png_import_path := Path(src, "png")).is_dir():
        copytree(png_import_path, ICONS_PATH / "png", dirs_exist_ok=True)
        png_count = len(tuple(png_import_path.glob("*.png")))
    if (svg_import_path := Path(src, "svg")).is_dir():
        copytree(svg_import_path, ICONS_PATH / "svg", dirs_exist_ok=True)
        svg_count = len(tuple(svg_import_path.glob("*.svg")))

    return IconsImportStats(png_count, svg_count)


def _extract_upload_as_zip(upload_fp: Path, extract_into_fp: Path):
    with ZipFile(upload_fp, "r") as zip_file:
        zip_file.extractall(extract_into_fp)


def extract_upload(upload_fp: str | Path, extract_into_fp: Path):
    """
    extracts an uploaded compressed format,
    accepted formats are taken from VALID_UPLOAD_EXTENSIONS

        :param upload_fp: Location of the uploaded file
        :param extract_into_fp: Where to extract upload to
        :raises ValueError: When an unknown suffix is found
    """
    match upload_fp.suffixes:
        case [".zip"]:
            _extract_upload_as_zip(upload_fp, extract_into_fp)
        case _:
            # TODO throw custom exception
            raise ValueError("unknown file suffix, cannot guess file-type")
