import pytest

from dbterd.adapters.targets.mermaid import MermaidAdapter


class TestMermaidColumnTypes:
    @pytest.mark.parametrize(
        "input_type,expected",
        [
            ("string", None),
            ("struct<string a, string b>", "struct"),
            ("array<struct<string a, string b>>", "array"),
            ("array<struct<string a_id, string b_id>>", "array"),
        ],
    )
    def test_match_complex_column_type(self, input_type, expected):
        adapter = MermaidAdapter()
        assert adapter.match_complex_column_type(input_type) == expected

    @pytest.mark.parametrize(
        "input_type,expected",
        [
            ("string", "string"),
            ("struct<string a, string b>", "struct[OMITTED]"),
            ("array<struct<string a, string b>>", "array[OMITTED]"),
            ("array<struct<string a_id, string b_id>>", "array[OMITTED]"),
        ],
    )
    def test_replace_column_type(self, input_type, expected):
        adapter = MermaidAdapter()
        assert adapter.replace_column_type(input_type) == expected
