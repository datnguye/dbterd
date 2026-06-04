from enum import Enum
import json
import os
import re
import sys
from types import UnionType
from typing import Optional, Union, get_args, get_origin

from dbt_artifacts_parser import parser
from pydantic import BaseModel

from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def extract_artifact_version_from_file(schema_version: str) -> Optional[str]:
    """Extract version number from dbt_schema_version URL.

    Args:
        schema_version: Schema version URL like "https://schemas.getdbt.com/dbt/manifest/v12.json"

    Returns:
        Version string like "12", or None if extraction fails
    """
    # Match pattern like /v12.json or /v12/ with optional leading slash
    match = re.search(r"/?v(\d+)(?:\.json)?(?:/|$)", schema_version)
    if match:
        return match.group(1)
    return None


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


def open_json(fp: str) -> dict:
    """Json loading utility, leveraging long path fixes.

    Args:
        fp: File path to JSON file

    Returns:
        Parsed JSON as dictionary
    """
    return json.loads(load_file_contents(fp))


def relax_pydantic_models(artifact_module: object) -> None:
    """Relax every Pydantic model in a parser module to tolerate unknown fields.

    Switches each model's ``extra`` config from ``forbid`` to ``ignore`` so that
    fields added by newer dbt versions (under the same schema version number) no
    longer trip ``extra_forbidden`` validation errors. dbt 1.11, for example, added
    a ``config`` property to macro nodes while keeping ``manifest_version`` at 12.

    Args:
        artifact_module: The imported ``*_v{n}`` parser module to patch.
    """
    for attr_name in dir(artifact_module):
        candidate = getattr(artifact_module, attr_name, None)
        if isinstance(candidate, type) and issubclass(candidate, BaseModel):
            model_config = getattr(candidate, "model_config", None)
            if model_config is not None and model_config.get("extra") == "forbid":
                model_config["extra"] = "ignore"
                candidate.model_rebuild(force=True)


# Enum fields dbterd reads as enums (via ``<field>.value``) are always named ``type``
# — e.g. ``constraint.type.value``, ``entity.type.value``. We keep those as enums and
# widen every other enum-typed field to ``str`` so unknown values can't break parsing.
_CONSUMED_ENUM_FIELDS = frozenset({"type"})


def relax_enum_members(artifact_module: object) -> None:
    """Allow unknown enum values by widening non-consumed enum fields to plain strings.

    Newer dbt/adapter releases occasionally introduce enum values the pinned parser
    doesn't know about (e.g. ``javascript`` in ``supported_languages``), which raise
    enum validation errors. Such fields are widened to accept arbitrary strings.

    Fields that dbterd itself reads as enums (see ``_CONSUMED_ENUM_FIELDS``) are left
    untouched so downstream ``.value`` access keeps working.

    Args:
        artifact_module: The imported ``*_v{n}`` parser module to patch.
    """
    for attr_name in dir(artifact_module):
        candidate = getattr(artifact_module, attr_name, None)
        if not (isinstance(candidate, type) and issubclass(candidate, BaseModel)):
            continue

        rebuilt = False
        for field_name, field in candidate.model_fields.items():
            if field_name in _CONSUMED_ENUM_FIELDS:
                continue
            if _annotation_references_enum(field.annotation):
                field.annotation = _replace_enum_with_str(field.annotation)
                rebuilt = True
        if rebuilt:
            candidate.model_rebuild(force=True)


def _annotation_references_enum(annotation: object) -> bool:
    """Return True if a type annotation references an Enum, including within generics."""
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return True
    return any(_annotation_references_enum(arg) for arg in get_args(annotation))


def _replace_enum_with_str(annotation: object) -> object:
    """Rebuild an annotation with every Enum reference swapped for ``str``."""
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return str

    args = get_args(annotation)
    if not args:
        return annotation

    origin = get_origin(annotation)
    new_args = tuple(_replace_enum_with_str(arg) for arg in args)
    if origin is UnionType:
        return Union[new_args]
    return origin[new_args]


def patch_parser_compatibility(artifact: str = "catalog", artifact_version: Optional[int] = None) -> None:
    """
    Conditionally monkey patch dbt-artifacts-parser Pydantic models for compatibility.

    Relaxes every model in the versioned parser module so that newer dbt releases
    sharing the same schema version (e.g. dbt 1.11 still reporting manifest v12) can
    still be parsed. Two relaxations are applied:

    - ``extra=forbid`` becomes ``extra=ignore`` to tolerate newly added fields
      (such as the ``config`` property dbt 1.11 added to macro nodes).
    - Non-consumed enum fields widen to plain strings to tolerate newly added enum
      values (such as ``javascript`` in ``supported_languages``).

    Args:
        artifact: Artifact type ('manifest' or 'catalog'). Defaults to 'catalog'.
        artifact_version: Artifact schema version (e.g., 12 for v12). Required for patching.

    References:
        https://github.com/yu-iskw/dbt-artifacts-parser/issues/160
        https://github.com/yu-iskw/dbt-artifacts-parser/issues/219
    """
    try:
        artifact_module = __import__(
            f"dbt_artifacts_parser.parsers.{artifact}.{artifact}_v{artifact_version}",
            fromlist=["Metadata"],
        )
        relax_pydantic_models(artifact_module)
        relax_enum_members(artifact_module)

        artifact_class_name = f"{artifact.capitalize()}V{artifact_version}"
        artifact_class = getattr(artifact_module, artifact_class_name, None)
        if artifact_class and hasattr(artifact_class, "model_rebuild"):
            artifact_class.model_rebuild(force=True)

    except (ImportError, AttributeError) as e:
        logger.debug(f"Could not patch {artifact} v{artifact_version} metadata: {e}")


MAX_PATH_LENGTH_WITHOUT_PREFIX = 250


def convert_path(path: str) -> str:
    """
    Convert a path which might be >260 characters long, to one that will be writable/readable on Windows.
    On other platforms, this is a no-op.

    Args:
        path (str): Path string

    Returns:
        str: Converted path string

    """
    # some parts of python seem to append '\*.*' to strings, better safe than
    # sorry.
    if len(path) < MAX_PATH_LENGTH_WITHOUT_PREFIX:
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
    # I don't know exactly what he means, but I am inclined to believe him as
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


def read_manifest(path: str, version: Optional[int] = None, enable_compat_patch: bool = False) -> Manifest:
    """
    Reads in the manifest.json file, with optional version specification.

    Args:
        path (str): manifest.json file path
        version (int, optional): Manifest version. Defaults to None (auto-detect).
        enable_compat_patch (bool, optional): Enable compatibility monkey patching. Defaults to True.

    Returns:
        dict: Manifest dict

    """
    if enable_compat_patch and version:
        logger.info(f"Patching manifest v{version} for compatibility...")
        patch_parser_compatibility(artifact="manifest", artifact_version=version)

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


def read_catalog(path: str, version: Optional[int] = None, enable_compat_patch: bool = False) -> Catalog:
    """
    Reads in the catalog.json file, with optional version specification.

    Args:
        path (str): catalog.json file path
        version (int, optional): Catalog version. Defaults to None.
        enable_compat_patch (bool, optional): Enable compatibility monkey patching. Defaults to True.

    Returns:
        dict: Catalog dict

    """
    if enable_compat_patch and version:
        logger.info(f"Patching catalog v{version} for compatibility...")
        patch_parser_compatibility(artifact="catalog", artifact_version=version)

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


def write_json(data: str, path: str) -> None:
    """Persist json data to file.

    Args:
        data: Json string data
        path: File path
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write(data)
