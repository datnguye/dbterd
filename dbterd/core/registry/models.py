"""Plugin info dataclass for dbterd registry.

This module defines the PluginInfo dataclass for storing adapter metadata.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginInfo:
    """Metadata about a registered plugin."""

    name: str
    adapter_class: type
    description: str = ""
