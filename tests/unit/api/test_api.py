from pathlib import Path
from unittest import mock

from dbterd import default
from dbterd.api import DbtErd


class TestDbtErd:
    @mock.patch("dbterd.core.executor.Executor.run")
    def test_get_erd(self, mock_executor_run):
        mock_executor_run.return_value = "expected-result"
        assert DbtErd().get_erd() == "expected-result"

    @mock.patch("dbterd.core.executor.Executor.run")
    def test_get_model_erd(self, mock_executor_run):
        mock_executor_run.return_value = "expected-result"
        assert DbtErd().get_model_erd(node_unique_id="any") == "expected-result"

    def test_init_default(self):
        actual = DbtErd()
        actual_dict = dict(vars(actual))
        del actual_dict["executor"]
        assert actual_dict == {
            "params": {
                "api": True,
                "select": [],
                "exclude": [],
                "resource_type": default.default_resource_types(),
                "algo": default.default_algo(),
                "entity_name_format": default.default_entity_name_format(),
                "omit_columns": False,
                "artifacts_dir": Path.cwd(),
                "target": default.default_target(),
            }
        }
        assert actual.executor.ctx.command.name == "run"
