"""Pytest configuration for dbterd unit tests."""

pytest_plugins = [
    "tests.unit.fixtures.executor",
    "tests.unit.fixtures.models",
    "tests.unit.fixtures.test_data",
]
