from typing import List, Tuple, Union

from dbterd.adapters.meta import Ref, Table
from dbterd.types import Catalog, Manifest


def parse_metadata(data, **kwargs) -> Tuple[List[Table], List[Ref]]:
    raise NotImplementedError()


def parse(
    manifest: Manifest, catalog: Union[str, Catalog], **kwargs
) -> Tuple[List[Table], List[Ref]]:
    raise NotImplementedError()


def find_related_nodes_by_id(
    manifest: Union[Manifest, dict], node_unique_id: str, type: str = None, **kwargs
) -> List[str]:
    raise NotImplementedError()
