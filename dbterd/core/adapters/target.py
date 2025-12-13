"""Base class for target adapters.

This module provides the abstract base class that all target format adapters
must inherit from. It implements common functionality and defines the interface
that subclasses must implement.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from dbterd.core.models import Ref, Table


class BaseTargetAdapter(ABC):
    """Base class for all target format adapters.

    Target adapters are responsible for converting parsed dbt artifacts
    (tables and relationships) into specific ERD output formats like
    DBML, Mermaid, GraphViz, etc.

    Subclasses must implement:
        - build_erd: Build the format-specific ERD content
        - format_table: Format a single table
        - format_relationship: Format a single relationship

    Class attributes to override:
        - file_extension: Output file extension (e.g., ".dbml")
        - default_filename: Default output filename (e.g., "output.dbml")
        - RELATIONSHIP_SYMBOLS: Dict mapping relationship types to symbols
        - DEFAULT_SYMBOL: Default symbol when type not found

    """

    file_extension: str = ""
    default_filename: str = "output"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {}
    DEFAULT_SYMBOL: str = ""

    def run(self, tables: list[Table], relationships: list[Ref], **kwargs) -> tuple[str, str]:
        """Build ERD output from parsed tables and relationships.

        This is the main entry point called by the Executor.

        Args:
            tables: List of parsed Table objects
            relationships: List of parsed Ref objects
            **kwargs: Additional options including:
                output_file_name: Custom output filename

        Returns:
            Tuple of (filename, content)

        """
        output_file = kwargs.get("output_file_name") or self.default_filename
        content = self.build_erd(tables, relationships, **kwargs)
        return (output_file, content)

    @abstractmethod
    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build format-specific ERD content.

        Subclasses must implement this method to generate the actual
        ERD output string in their specific format.

        Args:
            tables: List of parsed Table objects
            relationships: List of parsed Ref objects
            **kwargs: Additional options

        Returns:
            ERD content string

        """
        pass

    @abstractmethod
    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table in the target format.

        Args:
            table: Table object to format
            **kwargs: Additional options

        Returns:
            Formatted table string

        """
        pass

    @abstractmethod
    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship in the target format.

        Args:
            relationship: Ref object to format
            **kwargs: Additional options

        Returns:
            Formatted relationship string

        """
        pass

    def get_rel_symbol(self, relationship_type: str) -> str:
        """Get the format-specific relationship symbol.

        Maps relationship type codes to format-specific symbols.
        If the type is not found in RELATIONSHIP_SYMBOLS, returns DEFAULT_SYMBOL.

        Args:
            relationship_type: Relationship type code (e.g., "1n", "n1", "nn")

        Returns:
            Format-specific relationship symbol

        """
        return self.RELATIONSHIP_SYMBOLS.get(relationship_type, self.DEFAULT_SYMBOL)
