"""Registration decorators for dbterd adapters.

This module provides decorators for auto-registering target and algorithm adapters.
"""

from dbterd.core.registry.plugin_registry import PluginRegistry


def register_target(name: str, description: str = ""):
    """
    Decorator for registering a target adapter class.

    Args:
        name: Unique name for the target
        description: Optional description of the target format

    Returns:
        Decorator function

    Example:
        @register_target("dbml", description="Database Markup Language format")
        class DbmlAdapter(BaseTargetAdapter):
            ...

    """

    def decorator(cls: type) -> type:
        PluginRegistry.register_target(name, cls, description)
        return cls

    return decorator


def register_algo(name: str, description: str = ""):
    """
    Decorator for registering an algorithm adapter class.

    Args:
        name: Unique name for the algorithm
        description: Optional description of the algorithm

    Returns:
        Decorator function

    Example:
        @register_algo("test_relationship", description="Detect relationships via dbt tests")
        class TestRelationshipAlgo(BaseAlgoAdapter):
            ...

    """

    def decorator(cls: type) -> type:
        PluginRegistry.register_algo(name, cls, description)
        return cls

    return decorator
