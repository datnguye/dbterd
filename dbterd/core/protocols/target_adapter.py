"""Target adapter protocol interface for dbterd.

This module defines the interface that all target format adapters must implement.
"""

from typing import Protocol, runtime_checkable

from dbterd.core.models import Ref, Table
from dbterd.types import Catalog, Manifest


@runtime_checkable
class TargetAdapter(Protocol):
    """Interface for target format adapters (e.g., DBML, Mermaid, GraphViz)."""

    file_extension: str
    default_filename: str

    def run(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[str, str]:
        """
        Parse dbt artifacts and export ERD file.

        Args:
            manifest: Manifest json
            catalog: Catalog json
            **kwargs: Additional options

        Returns:
            Tuple of (filename, content)

        """
        ...

    def parse(self, manifest: Manifest, catalog: Catalog, **kwargs) -> str:
        """
        Get the ERD content from dbt artifacts.

        Args:
            manifest: Manifest json
            catalog: Catalog json
            **kwargs: Additional options

        Returns:
            ERD content string

        """
        ...

    def get_rel_symbol(self, relationship_type: str) -> str:
        """
        Get format-specific relationship symbol.

        Args:
            relationship_type: Relationship type code (e.g., "1n", "n1", "nn")

        Returns:
            Format-specific relationship symbol

        """
        ...

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """
        Build format-specific ERD content.

        Args:
            tables: List of parsed tables
            relationships: List of parsed relationships
            **kwargs: Additional options

        Returns:
            ERD content string

        """
        ...
