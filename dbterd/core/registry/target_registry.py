from typing import Any

from dbterd.adapters.targets._protocol import TargetProtocol


class TargetRegistry:
    """Registry for managing target formatters.

    This registry stores and manages target format implementations,
    providing centralized access and validation.
    """

    def __init__(self) -> None:
        """Initialize the target registry."""
        self._targets: dict[str, type[TargetProtocol]] = {}
        self._instances: dict[str, TargetProtocol] = {}

    def register(self, name: str, target_class: type[TargetProtocol]) -> None:
        """Register a new target formatter.

        Args:
            name: Unique identifier for the target
            target_class: Class implementing TargetProtocol

        Raises:
            ValueError: If target doesn't implement required protocol
        """
        if not self._validates_protocol(target_class):
            raise ValueError(f"Target {target_class.__name__} does not implement TargetProtocol")
        self._targets[name] = target_class

    def get(self, name: str) -> TargetProtocol:
        """Get a target formatter instance.

        Args:
            name: Name of the registered target

        Returns:
            Instance of the requested target

        Raises:
            KeyError: If target not found in registry
        """
        if name not in self._instances:
            if name not in self._targets:
                available = ", ".join(self.list_available())
                raise KeyError(f"Target '{name}' not found in registry. Available targets: {available}")
            self._instances[name] = self._targets[name]()
        return self._instances[name]

    def list_available(self) -> list[str]:
        """List all registered target format names.

        Returns:
            List of registered target identifiers
        """
        return list(self._targets.keys())

    def _validates_protocol(self, target_class: type[Any]) -> bool:
        """Validate that a class implements the TargetProtocol.

        Args:
            target_class: Class to validate

        Returns:
            True if class implements all required methods and properties
        """
        required_methods = ["run"]
        required_properties = ["name", "file_extension"]

        for method in required_methods:
            if not hasattr(target_class, method):
                return False

        return all(hasattr(target_class, prop) for prop in required_properties)
