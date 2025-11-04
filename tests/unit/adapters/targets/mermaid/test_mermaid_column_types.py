import pytest

from dbterd.adapters.targets.mermaid import MermaidTarget


# Create target instance for tests
target = MermaidTarget()

complex_column_types = [
    ("string", None),
    ("struct<string a, string b>", "struct"),
    ("array<struct<string a, string b>>", "array"),
    ("array<struct<string a_id, string b_id>>", "array"),
]
column_types = [
    ("string", "string"),
    ("struct<string a, string b>", "struct[OMITTED]"),
    ("array<struct<string a, string b>>", "array[OMITTED]"),
    ("array<struct<string a_id, string b_id>>", "array[OMITTED]"),
]


@pytest.mark.parametrize("input,expected", complex_column_types)
def test_match_complex_column_type(input, expected):
    assert target.match_complex_column_type(input) == expected


@pytest.mark.parametrize("input,expected", column_types)
def test_replace_column_type(input, expected):
    assert target.replace_column_type(input) == expected
