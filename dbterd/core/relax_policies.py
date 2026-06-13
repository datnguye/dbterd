"""Built-in parser relaxation policies.

Each policy loosens artifact-parser Pydantic validation in a specific way so that
newer dbt releases (sharing the same schema version) can still be parsed. Policies
self-register via ``@register_relax_policy`` and are resolved by name from the
``relax-policies`` config; importing this module is what populates the registry.
"""

from collections.abc import Iterator
from enum import Enum
from types import UnionType
from typing import Union, get_args, get_origin

from pydantic import BaseModel

from dbterd.core.validation_policy import register_relax_policy


# Enum fields dbterd reads as enums (via ``<field>.value``) are always named ``type``
# — e.g. ``constraint.type.value``, ``entity.type.value``. We keep those as enums and
# widen every other enum-typed field to ``str`` so unknown values can't break parsing.
# Trade-off: a NEW value added to a kept ``type`` enum would still raise — acceptable,
# since keeping it as an enum is what lets the rest of dbterd rely on ``.value``.
_CONSUMED_ENUM_FIELDS = frozenset({"type"})


def _iter_pydantic_models(artifact_module: object) -> Iterator[type[BaseModel]]:
    """Yield every Pydantic model class defined in a parser module."""
    for attr_name in dir(artifact_module):
        candidate = getattr(artifact_module, attr_name, None)
        if isinstance(candidate, type) and issubclass(candidate, BaseModel):
            yield candidate


@register_relax_policy("relax_extra_fields")
def relax_pydantic_models(artifact_module: object) -> None:
    """Relax every Pydantic model in a parser module to tolerate unknown fields.

    Switches each model's ``extra`` config from ``forbid`` to ``ignore`` so that
    fields added by newer dbt versions (under the same schema version number) no
    longer trip ``extra_forbidden`` validation errors. dbt 1.11, for example, added
    a ``config`` property to macro nodes while keeping ``manifest_version`` at 12.

    Args:
        artifact_module: The imported ``*_v{n}`` parser module to patch.
    """
    for model in _iter_pydantic_models(artifact_module):
        model_config = getattr(model, "model_config", None)
        if model_config is not None and model_config.get("extra") == "forbid":
            model_config["extra"] = "ignore"
            model.model_rebuild(force=True)


@register_relax_policy("relax_enum_values")
def relax_enum_members(artifact_module: object) -> None:
    """Allow unknown enum values by widening non-consumed enum fields to plain strings.

    Newer dbt/adapter releases occasionally introduce enum values the pinned parser
    doesn't know about (e.g. ``javascript`` in ``supported_languages``), which raise
    enum validation errors. Such fields are widened to accept arbitrary strings.

    Fields named in ``_CONSUMED_ENUM_FIELDS`` are left untouched so downstream
    ``.value`` access keeps working.

    Args:
        artifact_module: The imported ``*_v{n}`` parser module to patch.
    """
    for model in _iter_pydantic_models(artifact_module):
        rebuilt = False
        for field_name, field in model.model_fields.items():
            if field_name in _CONSUMED_ENUM_FIELDS:
                continue
            if _annotation_references_enum(field.annotation):
                field.annotation = _replace_enum_with_str(field.annotation)
                rebuilt = True
        if rebuilt:
            model.model_rebuild(force=True)


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
    origin = get_origin(annotation)
    if not args or origin is None:
        # A bare type, or an annotation we can't safely reconstruct — leave as-is.
        return annotation

    new_args = tuple(_replace_enum_with_str(arg) for arg in args)
    if origin is UnionType:
        return Union[new_args]
    return origin[new_args]
