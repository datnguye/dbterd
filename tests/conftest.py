"""Configure pytest for the project."""

import warnings


pytest_plugins = [
    "tests.unit.fixtures.cli",
    "tests.unit.fixtures.executor",
    "tests.unit.fixtures.models",
    "tests.unit.fixtures.test_data",
]


def pytest_configure(config):
    """Configure pytest."""
    # Filter out the pydantic warnings from dbt-artifacts-parser
    warnings.filterwarnings(
        "ignore",
        message=r"Field \"model_unique_id\" in (ParsedMetric|Metric) has conflict with protected namespace \"model_\"",
        module="pydantic",
    )
