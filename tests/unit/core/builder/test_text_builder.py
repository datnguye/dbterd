from dbterd.core.builder.text_builder import TextERDBuilder
from dbterd.core.models import Column, Ref, Table


class TestTextERDBuilder:
    def test_basic_build(self):
        """Test basic text builder output."""
        builder = TextERDBuilder()
        builder.add_header("erDiagram")
        builder.add_section("-- Tables --")
        result = builder.build()
        assert result == "erDiagram\n-- Tables --\n"

    def test_build_with_custom_separator(self):
        """Test build with custom separator."""
        builder = TextERDBuilder()
        builder.add_section("line1")
        builder.add_section("line2")
        result = builder.build(separator="\n\n")
        assert result == "line1\n\nline2\n"

    def test_build_with_tables_and_relationships(self):
        """Test build with formatted tables and relationships."""
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

        builder = TextERDBuilder()
        builder.add_header("erDiagram")
        builder.add_tables([table], lambda t: f'"{t.name}" {{ id int }}')
        builder.add_relationships([ref], lambda r: f'"{r.table_map[0]}" --> "{r.table_map[1]}"')
        builder.add_footer("// end")

        result = builder.build()
        assert "erDiagram" in result
        assert '"test_table" { id int }' in result
        assert '"table1" --> "table2"' in result
        assert "// end" in result

    def test_clear(self):
        """Test clear resets builder state."""
        builder = TextERDBuilder()
        builder.add_section("content")
        builder.clear()
        result = builder.build()
        assert result == "\n"  # Empty content still returns trailing newline

    def test_method_chaining(self):
        """Test method chaining returns self."""
        builder = TextERDBuilder()
        result = (
            builder.add_header("header")
            .add_section("section")
            .add_tables([], lambda t: "")
            .add_relationships([], lambda r: "")
            .add_footer("footer")
        )
        assert result is builder
