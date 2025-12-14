"""Consolidated tests for get_rel_symbol across all target adapters.

This module tests the relationship symbol mapping for all target adapters
in a single place, reducing code duplication across individual adapter tests.
"""

import pytest

from tests.unit.fixtures.test_data import ADAPTER_REL_SYMBOL_CONFIGS, RELATIONSHIP_TYPES


def _generate_test_cases():
    """Generate test cases for all adapters and relationship types."""
    test_cases = []
    for adapter_class, symbols in ADAPTER_REL_SYMBOL_CONFIGS:
        for rel_type, symbol in zip(RELATIONSHIP_TYPES, symbols):
            test_cases.append((adapter_class, rel_type, symbol))
    return test_cases


class TestGetRelSymbol:
    """Consolidated tests for get_rel_symbol method across all target adapters."""

    @pytest.mark.parametrize(
        "adapter_class, relationship_type, expected_symbol",
        _generate_test_cases(),
        ids=lambda x: f"{x.__name__ if hasattr(x, '__name__') else x}",
    )
    def test_get_rel_symbol(self, adapter_class, relationship_type, expected_symbol):
        """Test that each adapter returns the correct symbol for each relationship type."""
        adapter = adapter_class()
        assert adapter.get_rel_symbol(relationship_type=relationship_type) == expected_symbol
