import click
import pytest

from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.adapters.targets.dbml import DbmlAdapter
from dbterd.core.executor import Executor


class TestFactory:
    @pytest.fixture
    def executor(self):
        return Executor(ctx=click.Context(command=click.Command("dummy")))

    def test_load_target_failed(self, executor):
        with pytest.raises(KeyError) as exc_info:
            executor.load_target(name="dummy-target")
        assert "Target 'dummy-target' not registered" in str(exc_info.value)

    def test_load_target(self, executor):
        adapter = executor.load_target(name="dbml")
        assert isinstance(adapter, DbmlAdapter)

    def test_load_algo_failed(self, executor):
        with pytest.raises(KeyError) as exc_info:
            executor.load_algo(name="dummy-algo")
        assert "Algo 'dummy-algo' not registered" in str(exc_info.value)

    def test_load_algo(self, executor):
        adapter = executor.load_algo(name="test_relationship")
        assert isinstance(adapter, TestRelationshipAlgo)

    def test_load_algo_with_rule_suffix(self, executor):
        adapter = executor.load_algo(name="test_relationship:relationships_table")
        assert isinstance(adapter, TestRelationshipAlgo)
