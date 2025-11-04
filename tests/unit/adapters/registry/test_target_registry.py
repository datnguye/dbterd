import pytest

from dbterd.core.registry.target_registry import TargetRegistry


class ValidTarget:
    """Valid target implementation for testing."""

    @property
    def name(self) -> str:
        return "valid_target"

    @property
    def file_extension(self) -> str:
        return ".txt"

    def run(self, *args, **kwargs):
        return "result"


class InvalidTarget:
    """Invalid target missing required methods."""

    @property
    def name(self) -> str:
        return "invalid_target"


class TestTargetRegistry:
    def test_register_valid_target(self):
        """Test registering a valid target."""
        registry = TargetRegistry()
        registry.register("test", ValidTarget)
        assert "test" in registry.list_available()

    def test_register_invalid_target(self):
        """Test registering an invalid target raises ValueError."""
        registry = TargetRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.register("invalid", InvalidTarget)
        assert "does not implement TargetProtocol" in str(exc_info.value)

    def test_get_target(self):
        """Test getting a target instance."""
        registry = TargetRegistry()
        registry.register("test", ValidTarget)

        target = registry.get("test")
        assert isinstance(target, ValidTarget)

        # Second call should return the same cached instance
        target2 = registry.get("test")
        assert target is target2

    def test_get_nonexistent_target(self):
        """Test getting a nonexistent target raises KeyError."""
        registry = TargetRegistry()
        registry.register("test", ValidTarget)

        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")
        assert "not found in registry" in str(exc_info.value)
        assert "Available targets:" in str(exc_info.value)

    def test_list_available(self):
        """Test listing available targets."""
        registry = TargetRegistry()
        registry.register("target1", ValidTarget)
        registry.register("target2", ValidTarget)

        available = registry.list_available()
        assert "target1" in available
        assert "target2" in available
        assert len(available) == 2
