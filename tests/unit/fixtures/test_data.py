"""Test data fixtures for adapter tests."""

import pytest

from dbterd.adapters.targets.d2 import D2Adapter
from dbterd.adapters.targets.dbml import DbmlAdapter
from dbterd.adapters.targets.drawdb import DrawdbAdapter
from dbterd.adapters.targets.graphviz import GraphvizAdapter
from dbterd.adapters.targets.mermaid import MermaidAdapter
from dbterd.adapters.targets.plantuml import PlantumlAdapter


# Common relationship types used across all adapters
RELATIONSHIP_TYPES = ("0n", "1n", "01", "11", "nn", "n1", "--irrelevant--")


@pytest.fixture
def complex_column_types():
    """Test data for complex column type matching.

    Returns list of (input, expected) tuples.
    """
    return [
        ("string", None),
        ("struct<string a, string b>", "struct"),
        ("array<struct<string a, string b>>", "array"),
        ("array<struct<string a_id, string b_id>>", "array"),
    ]


@pytest.fixture
def column_type_replacements():
    """Test data for column type replacement.

    Returns list of (input, expected) tuples.
    """
    return [
        ("string", "string"),
        ("struct<string a, string b>", "struct[OMITTED]"),
        ("array<struct<string a, string b>>", "array[OMITTED]"),
        ("array<struct<string a_id, string b_id>>", "array[OMITTED]"),
    ]


def _build_rel_symbols(symbols: tuple) -> list:
    """Build relationship type to symbol list from a tuple of symbols.

    Args:
        symbols: Tuple of symbols in order: (0n, 1n, 01, 11, nn, n1, default)
    """
    return list(zip(RELATIONSHIP_TYPES, symbols))


# Symbol mappings for each adapter (0n, 1n, 01, 11, nn, n1, default)
MERMAID_SYMBOLS = ("}o--|{", "||--|{", "}o--||", "||--||", "}|--|{", "}|--||", "}|--||")
DBML_SYMBOLS = ("<", "<", "-", "-", "<>", ">", ">")
D2_SYMBOLS = ("->", "->", "->", "->", "->", "->", "->")
GRAPHVIZ_SYMBOLS = ("->", "->", "->", "->", "->", "->", "->")
PLANTUML_SYMBOLS = ("}o--|{", "||--|{", "}o--||", "||--||", "}|--|{", "}|--||", "}|--||")
DRAWDB_SYMBOLS = (
    "One to many",
    "One to many",
    "One to one",
    "One to one",
    "Many to many",
    "Many to one",
    "Many to one",
)


@pytest.fixture
def mermaid_rel_symbols():
    """Relationship type to symbol mapping for Mermaid adapter."""
    return _build_rel_symbols(MERMAID_SYMBOLS)


@pytest.fixture
def dbml_rel_symbols():
    """Relationship type to symbol mapping for DBML adapter."""
    return _build_rel_symbols(DBML_SYMBOLS)


@pytest.fixture
def d2_rel_symbols():
    """Relationship type to symbol mapping for D2 adapter."""
    return _build_rel_symbols(D2_SYMBOLS)


@pytest.fixture
def graphviz_rel_symbols():
    """Relationship type to symbol mapping for Graphviz adapter."""
    return _build_rel_symbols(GRAPHVIZ_SYMBOLS)


@pytest.fixture
def plantuml_rel_symbols():
    """Relationship type to symbol mapping for PlantUML adapter."""
    return _build_rel_symbols(PLANTUML_SYMBOLS)


@pytest.fixture
def drawdb_rel_symbols():
    """Relationship type to symbol mapping for DrawDB adapter."""
    return _build_rel_symbols(DRAWDB_SYMBOLS)


# Adapter class to symbol mapping for consolidated testing
ADAPTER_REL_SYMBOL_CONFIGS = [
    (MermaidAdapter, MERMAID_SYMBOLS),
    (DbmlAdapter, DBML_SYMBOLS),
    (D2Adapter, D2_SYMBOLS),
    (GraphvizAdapter, GRAPHVIZ_SYMBOLS),
    (PlantumlAdapter, PLANTUML_SYMBOLS),
    (DrawdbAdapter, DRAWDB_SYMBOLS),
]
