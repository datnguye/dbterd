"""Protocol interfaces for dbterd adapters.

This module defines the interfaces that all target and algorithm adapters must implement.
Using Protocol enables structural subtyping (duck typing) while still enabling type checking.
"""

from dbterd.core.protocols.algo_adapter import AlgoAdapter
from dbterd.core.protocols.target_adapter import TargetAdapter


__all__ = [
    "AlgoAdapter",
    "TargetAdapter",
]
