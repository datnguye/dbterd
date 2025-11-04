import contextlib
import importlib
import inspect
from pathlib import Path

from dbterd.adapters.algos._protocol import AlgorithmProtocol
from dbterd.adapters.targets._protocol import TargetProtocol
from dbterd.core.registry.decorators import (
    ALGORITHM_REGISTRY_NAME,
    TARGET_REGISTRY_NAME,
)
from dbterd.core.registry.parser_registry import ParserRegistry
from dbterd.core.registry.target_registry import TargetRegistry


class RegistryManager:
    """Central registry manager for coordinating all parser and target registrations.

    This manager provides a unified interface for accessing both algorithm parsers
    and target formatters through their respective registries.
    """

    def __init__(self) -> None:
        """Initialize the registry manager with empty registries."""
        self.parser_registry = ParserRegistry()
        self.target_registry = TargetRegistry()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize registries with auto-discovered implementations.

        This method should be called once to populate registries with
        built-in parsers and targets.
        """
        if self._initialized:
            return

        self._auto_discover_parsers()
        self._auto_discover_targets()
        self._initialized = True

    def _discover_algorithms(self, package_path: str = "dbterd.adapters.algos") -> dict[str, type[AlgorithmProtocol]]:
        """Auto-discover algorithm implementations.

        Scans the specified package for Python modules and discovers classes
        marked with @register_algorithm decorator.

        Args:
            package_path: Python package path to scan

        Returns:
            Dictionary mapping algorithm names to their classes
        """
        discovered: dict[str, type[AlgorithmProtocol]] = {}

        try:
            # Get package directory
            package = importlib.import_module(package_path)
            if package.__file__ is None:
                return discovered

            package_dir = Path(package.__file__).parent

            # Scan for algorithm modules (exclude base.py and __init__.py)
            for file in package_dir.glob("*.py"):
                if file.stem in ("__init__", "_protocol"):
                    continue

                module_name = file.stem
                full_module_name = f"{package_path}.{module_name}"

                try:
                    module = importlib.import_module(full_module_name)

                    # Find classes marked with @register_algorithm
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if hasattr(obj, ALGORITHM_REGISTRY_NAME):
                            algo_name = getattr(obj, ALGORITHM_REGISTRY_NAME)
                            discovered[algo_name] = obj
                except ImportError:
                    continue
        except ImportError:
            pass

        return discovered

    def _discover_targets(self, package_path: str = "dbterd.adapters.targets") -> dict[str, type[TargetProtocol]]:
        """Auto-discover target implementations.

        Scans the specified package for Python modules and discovers classes
        marked with @register_target decorator.

        Args:
            package_path: Python package path to scan

        Returns:
            Dictionary mapping target names to their classes
        """
        discovered: dict[str, type[TargetProtocol]] = {}

        try:
            package = importlib.import_module(package_path)
            if package.__file__ is None:
                return discovered

            package_dir = Path(package.__file__).parent

            # Scan for target modules (exclude __init__.py and _protocol.py)
            for file in package_dir.glob("*.py"):
                if file.stem in ("__init__", "_protocol"):
                    continue

                module_name = file.stem
                full_module_name = f"{package_path}.{module_name}"

                try:
                    module = importlib.import_module(full_module_name)

                    # Find classes marked with @register_target
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if hasattr(obj, TARGET_REGISTRY_NAME):
                            target_name = getattr(obj, TARGET_REGISTRY_NAME)
                            discovered[target_name] = obj
                except ImportError:
                    continue
        except ImportError:
            pass

        return discovered

    def _auto_discover_parsers(self) -> None:
        """Auto-discover and register parser algorithms."""
        discovered = self._discover_algorithms()
        for name, parser_class in discovered.items():
            with contextlib.suppress(ValueError):
                # Skip invalid implementations
                self.parser_registry.register(name, parser_class)

    def _auto_discover_targets(self) -> None:
        """Auto-discover and register target formatters."""
        discovered = self._discover_targets()
        for name, target_class in discovered.items():
            with contextlib.suppress(ValueError):
                # Skip invalid implementations
                self.target_registry.register(name, target_class)

    def get_parser(self, name: str) -> AlgorithmProtocol:
        """Retrieve a registered parser algorithm.

        Args:
            name: Name of the parser to retrieve

        Returns:
            Instance of the requested parser

        Raises:
            KeyError: If parser not found in registry
        """
        if not self._initialized:
            self.initialize()
        return self.parser_registry.get(name)

    def get_target(self, name: str) -> TargetProtocol:
        """Retrieve a registered target formatter.

        Args:
            name: Name of the target to retrieve

        Returns:
            Instance of the requested target

        Raises:
            KeyError: If target not found in registry
        """
        if not self._initialized:
            self.initialize()
        return self.target_registry.get(name)

    def register_parser(self, name: str, parser_class: type[AlgorithmProtocol]) -> None:
        """Register a new parser algorithm.

        Args:
            name: Unique identifier for the parser
            parser_class: Class implementing AlgorithmProtocol

        Raises:
            ValueError: If parser doesn't implement required protocol
        """
        self.parser_registry.register(name, parser_class)

    def register_target(self, name: str, target_class: type[TargetProtocol]) -> None:
        """Register a new target formatter.

        Args:
            name: Unique identifier for the target
            target_class: Class implementing TargetProtocol

        Raises:
            ValueError: If target doesn't implement required protocol
        """
        self.target_registry.register(name, target_class)

    def list_parsers(self) -> list[str]:
        """List all available parser names.

        Returns:
            List of registered parser identifiers
        """
        if not self._initialized:
            self.initialize()
        return self.parser_registry.list_available()

    def list_targets(self) -> list[str]:
        """List all available target names.

        Returns:
            List of registered target identifiers
        """
        if not self._initialized:
            self.initialize()
        return self.target_registry.list_available()


# Global registry instance
registry = RegistryManager()
