from typing import Any

from dbterd.adapters.algos._protocol import AlgorithmProtocol


class ParserRegistry:
    """Registry for managing parser algorithms.

    This registry stores and manages algorithm implementations,
    providing centralized access and validation.
    """

    def __init__(self) -> None:
        """Initialize the parser registry."""
        self._parsers: dict[str, type[AlgorithmProtocol]] = {}
        self._instances: dict[str, AlgorithmProtocol] = {}

    def register(self, name: str, parser_class: type[AlgorithmProtocol]) -> None:
        """Register a new parser algorithm.

        Args:
            name: Unique identifier for the parser
            parser_class: Class implementing AlgorithmProtocol

        Raises:
            ValueError: If parser doesn't implement required protocol
        """
        if not self._validates_protocol(parser_class):
            raise ValueError(f"Parser {parser_class.__name__} does not implement AlgorithmProtocol")
        self._parsers[name] = parser_class

    def get(self, name: str) -> AlgorithmProtocol:
        """Get a parser instance (cached singleton).

        Args:
            name: Name of the registered parser

        Returns:
            Instance of the requested parser

        Raises:
            KeyError: If parser not found in registry
        """
        if name not in self._instances:
            if name not in self._parsers:
                available = ", ".join(self.list_available())
                raise KeyError(f"Parser '{name}' not found in registry. Available parsers: {available}")
            self._instances[name] = self._parsers[name]()
        return self._instances[name]

    def list_available(self) -> list[str]:
        """List all registered parser names.

        Returns:
            List of registered parser identifiers
        """
        return list(self._parsers.keys())

    def _validates_protocol(self, parser_class: type[Any]) -> bool:
        """Validate that a class implements the AlgorithmProtocol.

        Args:
            parser_class: Class to validate

        Returns:
            True if class implements all required methods and properties
        """
        required_methods = [
            "parse",
            "parse_metadata",
            "find_related_nodes_by_id",
        ]
        required_properties = ["name", "description"]

        for method in required_methods:
            if not hasattr(parser_class, method):
                return False

        return all(hasattr(parser_class, prop) for prop in required_properties)
