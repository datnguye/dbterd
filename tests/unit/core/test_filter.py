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
