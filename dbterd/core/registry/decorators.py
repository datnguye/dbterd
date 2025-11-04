from typing import Callable, Optional

from dbterd.adapters.algos._protocol import AlgorithmProtocol
from dbterd.adapters.targets._protocol import TargetProtocol


# Registry metadata attribute names
ALGORITHM_REGISTRY_NAME = "__algorithm_registry_name__"
TARGET_REGISTRY_NAME = "__target_registry_name__"


def register_algorithm(
    name: Optional[str] = None,
) -> Callable[[type[AlgorithmProtocol]], type[AlgorithmProtocol]]:
    """Decorator to mark algorithms for auto-registration.

    This decorator adds metadata to the class that the discovery
    mechanism will use to register it.

    Args:
        name: Optional custom name for the algorithm. If not provided,
              uses the class's 'name' property or class name.

    Returns:
        Decorator function

    Example:
        @register_algorithm("test_relationship")
        class TestRelationshipAlgorithm:
            ...
    """

    def decorator(cls: type[AlgorithmProtocol]) -> type[AlgorithmProtocol]:
        algo_name = name
        if algo_name is None:
            if hasattr(cls, "name"):
                # Try to get name from property
                try:
                    instance = cls()
                    algo_name = instance.name
                except Exception:
                    algo_name = cls.__name__.lower()
            else:
                algo_name = cls.__name__.lower()

        # Mark class with registry metadata
        setattr(cls, ALGORITHM_REGISTRY_NAME, algo_name)
        return cls

    return decorator


def register_target(
    name: Optional[str] = None,
) -> Callable[[type[TargetProtocol]], type[TargetProtocol]]:
    """Decorator to mark targets for auto-registration.

    This decorator adds metadata to the class that the discovery
    mechanism will use to register it.

    Args:
        name: Optional custom name for the target. If not provided,
              uses the class's 'name' property or class name.

    Returns:
        Decorator function

    Example:
        @register_target("dbml")
        class DBMLTarget:
            ...
    """

    def decorator(cls: type[TargetProtocol]) -> type[TargetProtocol]:
        target_name = name
        if target_name is None:
            if hasattr(cls, "name"):
                # Try to get name from property
                try:
                    instance = cls()
                    target_name = instance.name
                except Exception:
                    target_name = cls.__name__.lower()
            else:
                target_name = cls.__name__.lower()

        # Mark class with registry metadata
        setattr(cls, TARGET_REGISTRY_NAME, target_name)
        return cls

    return decorator
