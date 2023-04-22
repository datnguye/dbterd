from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Column:
    """Parsed Column object"""

    name: str = "unknown"
    data_type: str = "unknown"


@dataclass
class Table:
    """Parsed Table object"""

    name: str
    database: str
    schema: str
    columns: Optional[List[Column]] = None
    raw_sql: Optional[str] = None
    resource_type: str = "model"


@dataclass
class Ref:
    """Parsed Relationship object"""

    name: str
    table_map: Tuple[str, str]
    column_map: Tuple[str, str]
