from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Column:
    """
    Sample DBML: id varchar [primary key]
    """

    name: str = "unknown"
    data_type: str = "unknown"


@dataclass
class Table:
    """
    Sample DBML:
    Table posts {
        id varchar [primary key]
    }
    """

    name: str
    database: str
    schema: str
    columns: Optional[List[Column]] = None
    raw_sql: Optional[str] = None
    resource_type: str = "model"


@dataclass
class Ref:
    """Sample DBML: Ref: posts.user_id > users.id"""

    name: str
    table_map: Tuple[str, str]
    column_map: Tuple[str, str]
