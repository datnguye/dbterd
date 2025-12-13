"""Algorithm adapter protocol interface for dbterd.

This module defines the interface that all algorithm adapters must implement.
"""

from typing import Optional, Protocol, Union, runtime_checkable

from dbterd.core.models import Ref, Table
from dbterd.types import Catalog, Manifest


@runtime_checkable
class AlgoAdapter(Protocol):
    """Interface for algorithm adapters (e.g., test_relationship, semantic)."""

    def parse(self, manifest: Manifest, catalog: Union[str, Catalog], **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse dbt artifacts to extract tables and relationships.

        Args:
            manifest: Manifest json or metadata dict
            catalog: Catalog json or "metadata" string
            **kwargs: Additional options

        Returns:
            Tuple of (tables, relationships)

        """
        ...

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """
        Parse from dbt Cloud metadata API response.

        Args:
            data: Metadata API response dict
            **kwargs: Additional options

        Returns:
            Tuple of (tables, relationships)

        """
        ...

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """
        Find FK/PK models related to a given model.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type (local file or metadata)
            **kwargs: Additional options

        Returns:
            List of related manifest node unique IDs

        """
        ...
