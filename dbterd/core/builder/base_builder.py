"""Base ERD Builder interface.

This module defines the abstract base class for all ERD builders.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from dbterd.core.models import Ref, Table


class BaseERDBuilder(ABC):
    """Base class for ERD builders.

    Provides the interface for building ERD output in different formats.
    Subclasses must implement the build() method.

    All add_* methods append content to an internal list in call order.
    """

    def __init__(self) -> None:
        """Initialize the ERD builder."""
        self._content: list[Any] = []

    def add_header(self, header: Any) -> "BaseERDBuilder":
        """Add a header section at the beginning.

        Note: In text builders, header is inserted at position 0.
        In JSON builders, header is stored separately.

        Args:
            header: Header content (type depends on implementation)

        Returns:
            Self for method chaining

        """
        self._content.insert(0, header)
        return self

    def add_section(self, content: Any) -> "BaseERDBuilder":
        """Add a content section.

        Args:
            content: Section content (type depends on implementation)

        Returns:
            Self for method chaining

        """
        self._content.append(content)
        return self

    def add_tables(self, tables: list[Table], formatter: Callable[[Table], Any]) -> "BaseERDBuilder":
        """Add formatted table sections.

        Args:
            tables: List of Table objects to format
            formatter: Function that formats a Table

        Returns:
            Self for method chaining

        """
        for table in tables:
            self._content.append(formatter(table))
        return self

    def add_relationships(self, relationships: list[Ref], formatter: Callable[[Ref], Any]) -> "BaseERDBuilder":
        """Add formatted relationship sections.

        Args:
            relationships: List of Ref objects to format
            formatter: Function that formats a Ref

        Returns:
            Self for method chaining

        """
        for rel in relationships:
            self._content.append(formatter(rel))
        return self

    def add_footer(self, footer: Any) -> "BaseERDBuilder":
        """Add a footer section at the end.

        Args:
            footer: Footer content (type depends on implementation)

        Returns:
            Self for method chaining

        """
        self._content.append(footer)
        return self

    @abstractmethod
    def build(self) -> str:
        """Build and return the final ERD content."""
        pass

    def clear(self) -> "BaseERDBuilder":
        """Clear all content and reset the builder.

        Returns:
            Self for method chaining

        """
        self._content.clear()
        return self
