import json
from pathlib import Path
import subprocess
import tempfile

import pytest


SAMPLES_DIR = Path(__file__).parent.parent.parent / "samples"
EXPECTED_OUTPUTS_DIR = Path(__file__).parent / "expected_outputs"


@pytest.mark.integration
class TestDbterdRun:
    """Integration tests that run dbterd and compare outputs to expected results."""

    @pytest.mark.parametrize(
        "sample,target,algo,options,expected_file",
        [
            ("jaffle-shop", "dbml", "test_relationship", [], "output.dbml"),
            ("jaffle-shop", "mermaid", "test_relationship", [], "output.md"),
            ("dbt-constraints", "plantuml", "test_relationship", [], "output.plantuml"),
            ("facebookad", "drawdb", "test_relationship", [], "output.ddb"),
            (
                "fivetranlog",
                "mermaid",
                "test_relationship",
                ["--omit-columns"],
                "output.md",
            ),
            ("shopify", "dbml", "test_relationship", [], "output.dbml"),
        ],
    )
    def test_run_and_compare_output(
        self,
        sample: str,
        target: str,
        algo: str,
        options: list[str],
        expected_file: str,
    ) -> None:
        """Run dbterd with specified options and compare to expected output."""
        sample_dir = SAMPLES_DIR / sample
        expected_output_dir = EXPECTED_OUTPUTS_DIR / sample
        expected_output_path = expected_output_dir / expected_file

        assert sample_dir.exists(), f"Sample directory not found: {sample_dir}"
        assert expected_output_path.exists(), f"Expected output not found: {expected_output_path}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = [
                "dbterd",
                "run",
                "--artifacts-dir",
                str(sample_dir),
                "--target",
                target,
                "--algo",
                algo,
                "--output",
                tmp_dir,
                *options,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0, f"dbterd failed with code {result.returncode}: {result.stderr}"

            actual_output_path = Path(tmp_dir) / expected_file
            assert actual_output_path.exists(), f"Output file not created: {actual_output_path}"

            actual_content = actual_output_path.read_text()
            expected_content = expected_output_path.read_text()

            if expected_file.endswith(".ddb"):
                self._compare_ddb_outputs(actual_content, expected_content)
            else:
                assert actual_content == expected_content, f"Output mismatch for {sample}/{target}"

    @pytest.mark.parametrize(
        "sample,target,algo,entity_format,expected_dir,expected_file",
        [
            (
                "dbtresto",
                "mermaid",
                "semantic",
                None,
                "dbtresto",
                "output.md",
            ),
            (
                "dbtresto",
                "d2",
                "test_relationship",
                None,
                "dbtresto-d2",
                "output.d2",
            ),
            (
                "dbtresto",
                "graphviz",
                "test_relationship",
                "schema.table",
                "dbtresto-graphviz",
                "output.graphviz",
            ),
        ],
    )
    def test_run_with_entity_format(
        self,
        sample: str,
        target: str,
        algo: str,
        entity_format: str | None,
        expected_dir: str,
        expected_file: str,
    ) -> None:
        """Run dbterd with entity-name-format and compare to expected output."""
        sample_dir = SAMPLES_DIR / sample
        expected_output_dir = EXPECTED_OUTPUTS_DIR / expected_dir
        expected_output_path = expected_output_dir / expected_file

        assert sample_dir.exists(), f"Sample directory not found: {sample_dir}"
        assert expected_output_path.exists(), f"Expected output not found: {expected_output_path}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = [
                "dbterd",
                "run",
                "--artifacts-dir",
                str(sample_dir),
                "--target",
                target,
                "--algo",
                algo,
                "--output",
                tmp_dir,
            ]

            if entity_format:
                cmd.extend(["--entity-name-format", entity_format])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0, f"dbterd failed with code {result.returncode}: {result.stderr}"

            actual_output_path = Path(tmp_dir) / expected_file
            assert actual_output_path.exists(), f"Output file not created: {actual_output_path}"

            actual_content = actual_output_path.read_text()
            expected_content = expected_output_path.read_text()

            assert actual_content == expected_content, f"Output mismatch for {sample}/{target}"

    def _compare_ddb_outputs(self, actual: str, expected: str) -> None:
        """Compare DrawDB JSON outputs, ignoring dynamic fields like date."""
        actual_json = json.loads(actual)
        expected_json = json.loads(expected)

        # Remove dynamic fields that change between runs
        for data in [actual_json, expected_json]:
            data.pop("date", None)

        assert actual_json == expected_json, "DrawDB output mismatch"
