import pytest

from dbterd.adapters import adapter
from dbterd.adapters.targets import dbml


class TestFactory:
    def test_load_executor_failed(self):
        with pytest.raises(Exception):
            adapter.load_executor(name="dummy")

    def test_load_executor(self):
        assert adapter.load_executor(name="dbml") == dbml
