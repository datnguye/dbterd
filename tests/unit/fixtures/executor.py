"""Executor and CLI fixtures for testing executor and command components."""

import click
import pytest

from dbterd.core.executor import Executor


@pytest.fixture
def dummy_click_context():
    """A dummy click.Context for Executor initialization."""
    return click.Context(command=click.Command("dummy"))


@pytest.fixture
def dummy_executor(dummy_click_context):
    """Pre-configured Executor instance for testing.

    Usage:
        def test_something(dummy_executor):
            result = dummy_executor.some_method()
    """
    return Executor(ctx=dummy_click_context)
