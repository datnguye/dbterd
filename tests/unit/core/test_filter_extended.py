from dbterd.core import filter
from dbterd.core.models import Table


class TestFilterExtended:
    def test_is_selected_table_with_none_params(self):
        """Test is_selected_table with None parameters initialized to defaults."""
        # Create a test table
        table = Table(
            name="test_table",
            node_name="model.pkg.test_table",
            resource_type="model",
            database="test_db",
            schema="test_schema",
        )

        # Test with all parameters None
        result = filter.is_selected_table(table=table, select_rules=None, exclude_rules=None, resource_types=None)

        # Should be selected since resource_type defaults to ["model"]
        assert result is True

    def test_is_selected_table_with_resource_type_filter(self):
        """Test is_selected_table with resource_type filtering."""
        # Create a test table with source resource type
        table = Table(
            name="test_table",
            node_name="source.pkg.test_table",
            resource_type="source",
            database="test_db",
            schema="test_schema",
        )

        # Test with resource_types parameter not including "source"
        result = filter.is_selected_table(table=table, select_rules=[], exclude_rules=[], resource_types=["model"])

        # Should not be selected since resource_type is "source" but only "model" is in resource_types
        assert result is False

        # Test with resource_types parameter including "source"
        result = filter.is_selected_table(
            table=table, select_rules=[], exclude_rules=[], resource_types=["model", "source"]
        )

        # Should be selected since resource_type is "source" and "source" is in resource_types
        assert result is True

    def test_is_satisfied_by_name_with_empty_rule(self):
        """Test is_satisfied_by_name with empty rule."""
        table = Table(name="test_table", node_name="model.pkg.test_table", database="test_db", schema="test_schema")

        result = filter.is_satisfied_by_name(table=table, rule="")
        assert result is True

    def test_is_satisfied_by_schema_with_empty_rule(self):
        """Test is_satisfied_by_schema with empty rule."""
        table = Table(name="test_table", node_name="model.pkg.test_table", database="test_db", schema="test_schema")

        result = filter.is_satisfied_by_schema(table=table, rule="")
        assert result is True

    def test_is_satisfied_by_schema_with_full_qualification(self):
        """Test is_satisfied_by_schema with database.schema format."""
        table = Table(name="test_table", node_name="model.pkg.test_table", database="test_db", schema="test_schema")

        # Test with just schema name
        result = filter.is_satisfied_by_schema(table=table, rule="test_schema")
        assert result is True

        # Test with database.schema format
        result = filter.is_satisfied_by_schema(table=table, rule="test_db.test_schema")
        assert result is True

        # Test with incorrect database.schema
        result = filter.is_satisfied_by_schema(table=table, rule="wrong_db.test_schema")
        assert result is False

    def test_is_satisfied_by_wildcard_with_empty_rule(self):
        """Test is_satisfied_by_wildcard with empty rule."""
        table = Table(name="test_table", node_name="model.pkg.test_table", database="test_db", schema="test_schema")

        result = filter.is_satisfied_by_wildcard(table=table, rule="")
        assert result is True

    def test_is_satisfied_by_exposure_with_empty_rule(self):
        """Test is_satisfied_by_exposure with empty rule."""
        table = Table(
            name="test_table",
            node_name="model.pkg.test_table",
            database="test_db",
            schema="test_schema",
            exposures=["dashboard", "report"],
        )

        result = filter.is_satisfied_by_exposure(table=table, rule="")
        assert result is True

        # Test with matching exposure
        result = filter.is_satisfied_by_exposure(table=table, rule="dashboard")
        assert result is True

        # Test with non-matching exposure
        result = filter.is_satisfied_by_exposure(table=table, rule="nonexistent")
        assert result is False

    def test_has_unsupported_rule_with_none_rules(self):
        """Test has_unsupported_rule with None rules parameter."""
        # Test with None rules
        result, rule = filter.has_unsupported_rule(rules=None)
        assert result is False
        assert rule is None
