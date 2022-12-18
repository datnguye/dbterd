from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Column:
    """
    Sample: id varchar [primary key]
    """

    name: str
    data_type: str = "varchar"


@dataclass
class Table:
    """
    Sample:
    Table posts {
        id varchar [primary key]
    }
    """

    name: str
    columns: Optional[List[Column]] = None
    raw_sql: Optional[str] = None


@dataclass
class Ref:
    """Sample: posts.user_id > users.id"""

    name: str
    table_map: List[str]
    column_map: List[str]
