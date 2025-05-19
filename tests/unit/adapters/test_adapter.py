import pytest

from dbterd.adapters import adapter
from dbterd.adapters.algos import test_relationship
from dbterd.adapters.targets import dbml


class TestFactory:
    def test_load_target_failed(self):
        with pytest.raises(Exception) as exc_info:
            adapter.load_target(name="dummy-target")
        assert "Could not find adapter target type" in str(exc_info.value)

    def test_load_target(self):
        assert adapter.load_target(name="dbml") == dbml

    def test_load_algo_failed(self):
        with pytest.raises(Exception) as exc_info:
            adapter.load_algo(name="dummy-algo")
        assert "Could not find adapter algo" in str(exc_info.value)

    def test_load_algo(self):
        assert adapter.load_algo(name="test_relationship") == test_relationship
