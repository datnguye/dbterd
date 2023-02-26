from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Column:
    """
    Sample DBML: id varchar [primary key]
    """

    name: str
    data_type: str = "varchar"


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


@dataclass
class Ref:
    """Sample DBML: Ref: posts.user_id > users.id"""

    name: str
    table_map: List[str]
    column_map: List[str]
