import pytest

from dbterd.adapters import adapter
from dbterd.adapters.algos import test_relationship
from dbterd.adapters.targets import dbml


class TestFactory:
    def test_load_target_failed(self):
        with pytest.raises(Exception):
            adapter.load_target(name="dummy-target")

    def test_load_target(self):
        assert adapter.load_target(name="dbml") == dbml

    def test_load_algo_failed(self):
        with pytest.raises(Exception):
            adapter.load_algo(name="dummy-algo")

    def test_load_algo(self):
        assert adapter.load_algo(name="test_relationship") == test_relationship
