import json
from unittest.mock import patch

from click.testing import CliRunner
import pytest

from dbterd.cli.main import dbterd


@pytest.mark.parametrize("command,method", [("run", "run"), ("debug", "evaluate_kwargs")])
@pytest.mark.parametrize("policies", [[], ["relax_extra_fields", "relax_enum_values"]])
def test_config_policy_list_reaches_executor(tmp_path, monkeypatch, policies, command, method):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dbterd.yml").write_text(json.dumps({"relax-policies": policies}), encoding="utf-8")
    with patch(f"dbterd.cli.main.Executor.{method}", return_value={}) as run:
        result = CliRunner().invoke(dbterd, [command])
    assert result.exit_code == 0
    assert run.call_args.kwargs["relax_policies"] == policies


@pytest.mark.parametrize("command,method", [("run", "run"), ("debug", "evaluate_kwargs")])
@pytest.mark.parametrize("value", ["", "relax_extra_fields,relax_enum_values"])
def test_cli_policy_string_overrides_config_list(tmp_path, monkeypatch, value, command, method):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dbterd.yml").write_text("relax-policies: [relax_extra_fields]\n", encoding="utf-8")
    with patch(f"dbterd.cli.main.Executor.{method}", return_value={}) as run:
        result = CliRunner().invoke(dbterd, [command, "--relax-policies", value])
    assert result.exit_code == 0
    assert run.call_args.kwargs["relax_policies"] == value
