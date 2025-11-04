from dbterd.adapters.algos._protocol import AlgorithmProtocol
from dbterd.adapters.targets._protocol import TargetProtocol
from dbterd.core.registry.decorators import register_algorithm, register_target
from dbterd.core.registry.manager import RegistryManager, registry
from dbterd.core.registry.parser_registry import ParserRegistry
from dbterd.core.registry.target_registry import TargetRegistry


__all__ = [
    "AlgorithmProtocol",
    "ParserRegistry",
    "RegistryManager",
    "TargetProtocol",
    "TargetRegistry",
    "register_algorithm",
    "register_target",
    "registry",
]
