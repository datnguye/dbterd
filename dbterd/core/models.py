from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass
class Column:
    """Parsed Column object."""

    name: str = "unknown"
    data_type: str = "unknown"
    description: str = ""


@dataclass
class Table:
    """Parsed Table object."""

    name: str
    database: str
    schema: str
    columns: Optional[list[Column]] = None
    raw_sql: Optional[str] = None
    resource_type: str = "model"
    exposures: list[str] = field(default_factory=list)
    node_name: Optional[str] = None
    description: str = ""
    label: Optional[str] = None


@dataclass
class Ref:
    """Parsed Relationship object."""

    name: str
    table_map: tuple[str, str]
    column_map: tuple[str, str]
    type: str = "n1"
    relationship_label: Optional[str] = None


@dataclass
class SemanticEntity:
    """Parsed Semantic Model's Entity object."""

    semantic_model: str
    model: str
    entity_name: str
    entity_type: str
    column_name: str
    relationship_type: str


class SelectionType(Enum):
    START_WITH_NAME = ""
    EXACT_NAME = "exact"
    SCHEMA = "schema"
    WILDCARD = "wildcard"
    EXPOSURE = "exposure"
