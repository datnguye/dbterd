"""Plugin registry class for dbterd adapters.

This module provides the central registry for target and algorithm adapters.
"""

from typing import ClassVar

from dbterd.core.registry.models import PluginInfo


class PluginRegistry:
    """Central registry for target and algo adapters.

    This class maintains dictionaries of registered target and algorithm adapters.
    Adapters can be registered using the @register_target and @register_algo decorators,
    or by calling the register methods directly.

    Example:
        @register_target("dbml", description="DBML format")
        class DbmlAdapter(BaseTargetAdapter):
            ...

        # Later, to get the adapter:
        adapter_class = PluginRegistry.get_target("dbml")
        adapter = adapter_class()

    """

    _targets: ClassVar[dict[str, PluginInfo]] = {}
    _algos: ClassVar[dict[str, PluginInfo]] = {}

    @classmethod
    def _check_registered(cls, name: str, registry: dict[str, PluginInfo], registry_name: str) -> None:
        """Verify item is registered, raise KeyError if not.

        Args:
            name: Name of the item to check
            registry: Registry dictionary to check in
            registry_name: Human-readable name for error message
        """
        if name not in registry:
            available = list(registry.keys())
            raise KeyError(f"{registry_name} '{name}' not registered. Available: {available}")

    @classmethod
    def register_target(cls, name: str, adapter_class: type, description: str = "") -> None:
        """
        Register a target adapter.

        Args:
            name: Unique name for the target (e.g., "dbml", "mermaid")
            adapter_class: The adapter class to register
            description: Optional description of the target format

        """
        cls._targets[name] = PluginInfo(name=name, adapter_class=adapter_class, description=description)

    @classmethod
    def register_algo(cls, name: str, adapter_class: type, description: str = "") -> None:
        """
        Register an algorithm adapter.

        Args:
            name: Unique name for the algorithm (e.g., "test_relationship", "semantic")
            adapter_class: The adapter class to register
            description: Optional description of the algorithm

        """
        cls._algos[name] = PluginInfo(name=name, adapter_class=adapter_class, description=description)

    @classmethod
    def get_target(cls, name: str) -> type:
        """
        Get a registered target adapter class.

        Args:
            name: Name of the target to retrieve

        Returns:
            The adapter class

        Raises:
            KeyError: If target is not registered

        """
        cls._check_registered(name, cls._targets, "Target")
        return cls._targets[name].adapter_class

    @classmethod
    def get_algo(cls, name: str) -> type:
        """
        Get a registered algorithm adapter class.

        Args:
            name: Name of the algorithm to retrieve

        Returns:
            The adapter class

        Raises:
            KeyError: If algorithm is not registered

        """
        cls._check_registered(name, cls._algos, "Algo")
        return cls._algos[name].adapter_class

    @classmethod
    def has_target(cls, name: str) -> bool:
        """
        Check if a target is registered.

        Args:
            name: Name of the target to check

        Returns:
            True if registered, False otherwise

        """
        return name in cls._targets

    @classmethod
    def has_algo(cls, name: str) -> bool:
        """
        Check if an algorithm is registered.

        Args:
            name: Name of the algorithm to check

        Returns:
            True if registered, False otherwise

        """
        return name in cls._algos

    @classmethod
    def list_targets(cls) -> list[str]:
        """
        List all registered target names.

        Returns:
            List of registered target names

        """
        return list(cls._targets.keys())

    @classmethod
    def list_algos(cls) -> list[str]:
        """
        List all registered algorithm names.

        Returns:
            List of registered algorithm names

        """
        return list(cls._algos.keys())

    @classmethod
    def get_target_info(cls, name: str) -> PluginInfo:
        """
        Get full plugin info for a target.

        Args:
            name: Name of the target

        Returns:
            PluginInfo for the target

        Raises:
            KeyError: If target is not registered

        """
        cls._check_registered(name, cls._targets, "Target")
        return cls._targets[name]

    @classmethod
    def get_algo_info(cls, name: str) -> PluginInfo:
        """
        Get full plugin info for an algorithm.

        Args:
            name: Name of the algorithm

        Returns:
            PluginInfo for the algorithm

        Raises:
            KeyError: If algorithm is not registered

        """
        cls._check_registered(name, cls._algos, "Algo")
        return cls._algos[name]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered adapters. Mainly useful for testing."""
        cls._targets.clear()
        cls._algos.clear()
