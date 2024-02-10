import os
import json
import sys

from dbt_artifacts_parser import parser

from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def get_sys_platform():  # pragma: no cover
    return sys.platform


if get_sys_platform() == "win32":  # pragma: no cover
    from ctypes import WinDLL, c_bool
else:
    WinDLL = None  # pragma: no cover
    c_bool = None  # pragma: no cover


def load_file_contents(path: str, strip: bool = True) -> str:
    path = convert_path(path)
    with open(path, "rb") as handle:
        to_return = handle.read().decode("utf-8")

    if strip:
        to_return = to_return.strip()

    return to_return


def open_json(fp):
    """Json loading utility, leveraging long path fixes"""
    return json.loads(load_file_contents(fp))


def convert_path(path: str) -> str:
    """Convert a path which might be >260 characters long, to one that will be writable/readable on Windows.
    On other platforms, this is a no-op.

    Args:
        path (str): Path string

    Returns:
        str: Converted path string
    """
    # some parts of python seem to append '\*.*' to strings, better safe than
    # sorry.
    if len(path) < 250:
        return path
    if supports_long_paths():
        return path

    prefix = "\\\\?\\"
    # Nothing to do
    if path.startswith(prefix):
        return path

    path = win_prepare_path(path)

    # add the prefix. The check is just in case os.getcwd() does something
    # unexpected - I believe this if-state should always be True though!
    if not path.startswith(prefix):
        path = prefix + path
    return path


def supports_long_paths(windll_name="ntdll") -> bool:  # pragma: no cover
    if get_sys_platform() != "win32":
        return True
    # Eryk Sun says to use `WinDLL('ntdll')` instead of `windll.ntdll` because
    # of pointer caching in a comment here:
    # https://stackoverflow.com/a/35097999/11262881
    # I don't know exaclty what he means, but I am inclined to believe him as
    # he's pretty active on Python windows bugs!
    else:
        try:
            dll = WinDLL(windll_name)
        except OSError:  # I don't think this happens? you need ntdll to run python
            return False
        # not all windows versions have it at all
        if not hasattr(dll, "RtlAreLongPathsEnabled"):
            return False  # pragma: no cover
        # tell windows we want to get back a single unsigned byte (a bool).
        dll.RtlAreLongPathsEnabled.restype = c_bool
        return dll.RtlAreLongPathsEnabled()


def win_prepare_path(path: str) -> str:  # pragma: no cover
    """Given a windows path, prepare it for use by making sure it is absolute and normalized."""
    path = os.path.normpath(path)

    # if a path starts with '\', splitdrive() on it will return '' for the
    # drive, but the prefix requires a drive letter. So let's add the drive
    # letter back in.
    # Unless it starts with '\\'. In that case, the path is a UNC mount point
    # and splitdrive will be fine.
    if not path.startswith("\\\\") and path.startswith("\\"):
        curdrive = os.path.splitdrive(os.getcwd())[0]
        path = curdrive + path

    # now our path is either an absolute UNC path or relative to the current
    # directory. If it's relative, we need to make it absolute or the prefix
    # won't work. `ntpath.abspath` allegedly doesn't always play nice with long
    # paths, so do this instead.
    if not os.path.splitdrive(path)[0]:
        path = os.path.join(os.getcwd(), path)

    return path


def read_manifest(path: str, version: int = None) -> Manifest:
    """Reads in the manifest.json file, with optional version specification

    Args:
        path (str): manifest.json file path
        version (int, optional): Manifest version. Defaults to None.

    Returns:
        dict: Manifest dict
    """
    _dict = open_json(f"{path}/manifest.json")
    default_parser = "parse_manifest"
    parser_version = f"parse_manifest_v{version}" if version else default_parser
    if not hasattr(parser, parser_version):
        logger.warning(
            "Manifest version is NOT SUPPORTED in current `dbt-artifacts-parser` package. \n"
            "Please help to try `-mv {version}` option with other value, OR upgrade the package:\n"
            "\tpip install dbt-artifacts-parser --upgrade\n"
            "Try falling back to the latest one..."
        )
        parser_version = default_parser
    parse_func = getattr(parser, parser_version)
    return parse_func(manifest=_dict)


def read_catalog(path: str, version: int = None) -> Catalog:
    """Reads in the catalog.json file, with optional version specification

    Args:
        path (str): catalog.json file path
        version (int, optional): Catalog version. Defaults to None.

    Returns:
        dict: Catalog dict
    """
    _dict = open_json(f"{path}/catalog.json")
    default_parser = "parse_catalog"
    parser_version = f"parse_catalog_v{version}" if version else default_parser
    if not hasattr(parser, parser_version):
        logger.warning(
            "Catalog version is NOT SUPPORTED in current `dbt-artifacts-parser` package. \n"
            "Please help to try `-mv {version}` option with other value, OR upgrade the package:\n"
            "\tpip install dbt-artifacts-parser --upgrade\n"
            "Try falling back to the latest one..."
        )
        parser_version = default_parser
    parse_func = getattr(parser, parser_version)
    return parse_func(catalog=_dict)


def write_json(data, path: str):
    """Persist json data to file

    Args:
        data (json): Json data
        path (str): File path
    """
    with open(path, "w") as file:
        file.write(data)
