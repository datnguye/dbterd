from pathlib import Path

from dbterd import default
from dbterd.api import DbtErd


class TestDbtErd:
    def test_init_default(self):
        actual = DbtErd()
        actual_dict = dict(vars(actual))
        del actual_dict["executor"]
        assert actual_dict == dict(
            params=dict(
                api=True,
                select=[],
                exclude=[],
                resource_type=default.default_resource_types(),
                algo=default.deafult_algo(),
                entity_name_format=default.default_entity_name_format(),
                omit_columns=False,
                artifacts_dir=Path.cwd(),
                target=default.default_target(),
            )
        )
        assert actual.executor.ctx.command.name == "run"
