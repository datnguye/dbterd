from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


@dataclass
class Column:
    """Parsed Column object"""

    name: str = "unknown"
    data_type: str = "unknown"
    description: str = ""


@dataclass
class Table:
    """Parsed Table object"""

    name: str
    database: str
    schema: str
    columns: Optional[List[Column]] = None
    raw_sql: Optional[str] = None
    resource_type: str = "model"
    exposures: Optional[List[str]] = field(default_factory=lambda: [])
    node_name: str = None
    description: str = ""


@dataclass
class Ref:
    """Parsed Relationship object"""

    name: str
    table_map: Tuple[str, str]
    column_map: Tuple[str, str]
    type: str = "n1"


class SelectionType(Enum):
    START_WITH_NAME = ""
    EXACT_NAME = "exact"
    SCHEMA = "schema"
    WILDCARD = "wildcard"
    EXPOSURE = "exposure"
