"""Test data fixtures for adapter tests."""

import pytest


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


@pytest.fixture
def mermaid_rel_symbols():
    """Relationship type to symbol mapping for Mermaid adapter."""
    return [
        ("0n", "}o--|{"),
        ("1n", "||--|{"),
        ("01", "}o--||"),
        ("11", "||--||"),
        ("nn", "}|--|{"),
        ("n1", "}|--||"),
        ("--irrelevant--", "}|--||"),
    ]


@pytest.fixture
def dbml_rel_symbols():
    """Relationship type to symbol mapping for DBML adapter."""
    return [
        ("0n", "<"),
        ("1n", "<"),
        ("01", "-"),
        ("11", "-"),
        ("nn", "<>"),
        ("n1", ">"),
        ("--irrelevant--", ">"),
    ]


@pytest.fixture
def d2_rel_symbols():
    """Relationship type to symbol mapping for D2 adapter."""
    return [
        ("0n", "->"),
        ("1n", "->"),
        ("01", "->"),
        ("11", "->"),
        ("nn", "->"),
        ("n1", "->"),
        ("--irrelevant--", "->"),
    ]


@pytest.fixture
def graphviz_rel_symbols():
    """Relationship type to symbol mapping for Graphviz adapter."""
    return [
        ("0n", "->"),
        ("1n", "->"),
        ("01", "->"),
        ("11", "->"),
        ("nn", "->"),
        ("n1", "->"),
        ("--irrelevant--", "->"),
    ]


@pytest.fixture
def plantuml_rel_symbols():
    """Relationship type to symbol mapping for PlantUML adapter."""
    return [
        ("0n", "}o--|{"),
        ("1n", "||--|{"),
        ("01", "}o--||"),
        ("11", "||--||"),
        ("nn", "}|--|{"),
        ("n1", "}|--||"),
        ("--irrelevant--", "}|--||"),
    ]
