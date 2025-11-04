import pytest

from dbterd.core.registry.parser_registry import ParserRegistry


class ValidParser:
    """Valid parser implementation for testing."""

    @property
    def name(self) -> str:
        return "valid_parser"

    @property
    def description(self) -> str:
        return "A valid parser"

    def parse(self, *args, **kwargs):
        return []

    def parse_metadata(self, *args, **kwargs):
        return []

    def find_related_nodes_by_id(self, *args, **kwargs):
        return []


class InvalidParser:
    """Invalid parser missing required methods."""

    @property
    def name(self) -> str:
        return "invalid_parser"


class TestParserRegistry:
    def test_register_valid_parser(self):
        """Test registering a valid parser."""
        registry = ParserRegistry()
        registry.register("test", ValidParser)
        assert "test" in registry.list_available()

    def test_register_invalid_parser(self):
        """Test registering an invalid parser raises ValueError."""
        registry = ParserRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.register("invalid", InvalidParser)
        assert "does not implement AlgorithmProtocol" in str(exc_info.value)

    def test_get_parser(self):
        """Test getting a parser instance."""
        registry = ParserRegistry()
        registry.register("test", ValidParser)

        parser = registry.get("test")
        assert isinstance(parser, ValidParser)

        # Second call should return the same cached instance
        parser2 = registry.get("test")
        assert parser is parser2

    def test_get_nonexistent_parser(self):
        """Test getting a nonexistent parser raises KeyError."""
        registry = ParserRegistry()
        registry.register("test", ValidParser)

        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")
        assert "not found in registry" in str(exc_info.value)
        assert "Available parsers:" in str(exc_info.value)

    def test_list_available(self):
        """Test listing available parsers."""
        registry = ParserRegistry()
        registry.register("parser1", ValidParser)
        registry.register("parser2", ValidParser)

        available = registry.list_available()
        assert "parser1" in available
        assert "parser2" in available
        assert len(available) == 2
