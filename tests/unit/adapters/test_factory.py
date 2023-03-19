import pytest

from dbterd.adapters import factory
from dbterd.adapters.targets import dbml


class TestFactory:
    def test_load_executor_failed(self):
        with pytest.raises(Exception):
            factory.load_executor(name="dummy")

    def test_load_executor(self):
        assert factory.load_executor(name="dbml") == dbml
