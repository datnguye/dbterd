import pytest
from dbterd.cli.main import dbterdRunner


class TestRunner:
    @pytest.fixture
    def dbterd(self) -> dbterdRunner:
        return dbterdRunner()

    def test_group_invalid_option(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["--invalid-option"])

    def test_command_invalid_option(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["run", "--invalid-option"])

    def test_invalid_command(self, dbterd: dbterdRunner) -> None:
        with pytest.raises(Exception):
            dbterd.invoke(["invalid-command"])

    def test_invoke_version(self, dbterd: dbterdRunner) -> None:
        dbterd.invoke(["--version"])

    def test_invoke_help(self, dbterd: dbterdRunner) -> None:
        dbterd.invoke(["-h"])
        dbterd.invoke(["--help"])
