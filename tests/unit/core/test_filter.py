import pytest

from dbterd.core import filter
from dbterd.core.models import Table


class TestFilter:
    @pytest.mark.parametrize(
        "rule, expected",
        [
            ([], (False, None)),
            (["dummy_name"], (False, None)),
            (["schema:dummy_name"], (False, None)),
            (["exact:dummy_name"], (False, None)),
            (["exposure:dummy_name"], (False, None)),
            (["dummy:dummy_name"], (True, "dummy")),
        ],
    )
    def test_has_unsupported_rule(self, rule, expected):
        actual = filter.has_unsupported_rule(rules=rule)
        assert actual == expected

    @pytest.mark.parametrize(
        "table, rule, expected",
        [
            (
                Table(
                    name="irrelevant",
                    node_name="model.dummy.table1",
                    database="dummydb",
                    schema="dummyschema",
                ),
                "",
                True,
            ),
            (
                Table(
                    name="irrelevant",
                    node_name="model.dummy.table1",
                    database="dummydb",
                    schema="dummyschema",
                ),
                "table1",
                False,
            ),
            (
                Table(
                    name="irrelevant",
                    node_name="model.dummy.table1",
                    database="dummydb",
                    schema="dummyschema",
                ),
                "model.dummy.table1",
                True,
            ),
            (
                Table(
                    name="irrelevant",
                    node_name="model.dummy.Table1",
                    database="dummydb",
                    schema="dummyschema",
                ),
                "model.dummy.table1",
                True,
            ),
        ],
    )
    def test_is_satisfied_by_exact(self, table, rule, expected):
        actual = filter.is_satisfied_by_exact(table=table, rule=rule)
        assert actual == expected

    @pytest.mark.parametrize(
        "rule",
        [
            "model.dbt_VDE.V_F_ORDERS",
            "model.dbt_vde.v_f_orders",
            "model.dbt_VDE.V_F",
            "wildcard:*V_F_ORDERS*",
            "wildcard:*v_f_orders*",
        ],
    )
    def test_rules_match_node_names_with_capitals(self, rule):
        table = Table(
            name="irrelevant",
            node_name="model.dbt_VDE.V_F_ORDERS",
            database="dummydb",
            schema="dummyschema",
            resource_type="model",
        )
        assert filter.is_selected_table(table, select_rules=[rule])
        assert not filter.is_selected_table(table, exclude_rules=[rule])

    def test_name_rule_still_rejects_other_node_names_with_capitals(self):
        table = Table(
            name="irrelevant",
            node_name="model.dbt_VDE.V_F_ORDERS",
            database="dummydb",
            schema="dummyschema",
            resource_type="model",
        )
        assert not filter.is_selected_table(table, select_rules=["model.dbt_VDE.V_F_CUSTOMERS"])
