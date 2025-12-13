import json

from dbterd.core.builder.json_builder import JsonERDBuilder
from dbterd.core.models import Column, Ref, Table


class TestJsonERDBuilder:
    def test_basic_build_with_header_only(self):
        """Test basic build with header only."""
        builder = JsonERDBuilder()
        builder.add_header({"author": "test"})
        result = builder.build(schema={"$header": None})
        parsed = json.loads(result)
        assert parsed == {"author": "test"}

    def test_build_with_tables_and_relationships(self):
        """Test build with tables and relationships."""
        table = Table(
            name="test_table",
            node_name="model.test.table",
            database="db",
            schema="schema",
            columns=[Column(name="id", data_type="int")],
            raw_sql="",
        )
        ref = Ref(
            name="test_ref",
            table_map=["table1", "table2"],
            column_map=["col1", "col2"],
        )

        builder = JsonERDBuilder()
        builder.add_header({"author": "test"})
        builder.add_tables([table], lambda t: {"name": t.name})
        builder.add_relationships([ref], lambda r: {"name": r.name})
        builder.add_footer({"version": "1.0"})

        schema = {
            "$header": None,
            "tables": "$tables",
            "relationships": "$relationships",
            "$footer": None,
        }
        result = builder.build(schema=schema)
        parsed = json.loads(result)

        assert parsed["author"] == "test"
        assert parsed["tables"] == [{"name": "test_table"}]
        assert parsed["relationships"] == [{"name": "test_ref"}]
        assert parsed["version"] == "1.0"

    def test_build_with_custom_schema(self):
        """Test build with custom schema."""
        builder = JsonERDBuilder()
        builder.add_header({"author": "test", "title": "Test ERD"})
        builder.add_tables(
            [
                Table(
                    name="t1",
                    node_name="m.t1",
                    database="db",
                    schema="sch",
                    columns=[],
                    raw_sql="",
                )
            ],
            lambda t: {"name": t.name},
        )

        schema = {
            "$header": None,
            "entities": "$tables",
            "refs": "$relationships",
            "extra": "value",
        }
        result = builder.build(schema=schema)
        parsed = json.loads(result)

        assert parsed["author"] == "test"
        assert parsed["title"] == "Test ERD"
        assert parsed["entities"] == [{"name": "t1"}]
        assert parsed["refs"] == []
        assert parsed["extra"] == "value"

    def test_build_with_footer_in_schema(self):
        """Test build with $footer placeholder in schema."""
        builder = JsonERDBuilder()
        builder.add_header({"author": "test"})
        builder.add_footer({"database": "postgres", "notes": []})

        schema = {
            "$header": None,
            "tables": "$tables",
            "$footer": None,
        }
        result = builder.build(schema=schema)
        parsed = json.loads(result)

        assert parsed["author"] == "test"
        assert parsed["tables"] == []
        assert parsed["database"] == "postgres"
        assert parsed["notes"] == []

    def test_add_section(self):
        """Test add_section merges into footer."""
        builder = JsonERDBuilder()
        builder.add_section({"custom_key": "custom_value"})

        schema = {"$footer": None}
        result = builder.build(schema=schema)
        parsed = json.loads(result)

        assert parsed["custom_key"] == "custom_value"

    def test_add_section_with_non_dict(self):
        """Test add_section ignores non-dict values."""
        builder = JsonERDBuilder()
        builder.add_section("not a dict")  # type: ignore

        result = builder.build(schema={"$footer": None})
        parsed = json.loads(result)
        assert parsed == {}

    def test_add_header_with_non_dict(self):
        """Test add_header ignores non-dict values."""
        builder = JsonERDBuilder()
        builder.add_header("not a dict")  # type: ignore

        result = builder.build(schema={"$header": None})
        parsed = json.loads(result)
        assert parsed == {}

    def test_add_footer_with_non_dict(self):
        """Test add_footer ignores non-dict values."""
        builder = JsonERDBuilder()
        builder.add_footer("not a dict")  # type: ignore

        result = builder.build(schema={"$footer": None})
        parsed = json.loads(result)
        assert parsed == {}

    def test_clear(self):
        """Test clear resets all internal state."""
        builder = JsonERDBuilder()
        builder.add_header({"author": "test"})
        builder.add_tables(
            [
                Table(
                    name="t1",
                    node_name="m.t1",
                    database="db",
                    schema="sch",
                    columns=[],
                    raw_sql="",
                )
            ],
            lambda t: {"name": t.name},
        )
        builder.add_footer({"version": "1.0"})

        builder.clear()
        result = builder.build(schema={"$header": None, "tables": "$tables", "$footer": None})
        parsed = json.loads(result)

        assert parsed == {"tables": []}

    def test_method_chaining(self):
        """Test method chaining returns self."""
        builder = JsonERDBuilder()
        result = (
            builder.add_header({"a": 1})
            .add_section({"b": 2})
            .add_tables([], lambda t: {})
            .add_relationships([], lambda r: {})
            .add_footer({"c": 3})
        )
        assert result is builder
