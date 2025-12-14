import click
import pytest

from dbterd.core.executor import Executor


class TestBaseExtended:
    def test_check_if_any_unsupported_selection_with_none_params(self):
        """Test _check_if_any_unsupported_selection with None parameters."""
        worker = Executor(ctx=click.Context(command=click.Command("dummy")))

        # Test with None select and None exclude
        worker._check_if_any_unsupported_selection(select=None, exclude=None)

        # Test with empty select and None exclude
        worker._check_if_any_unsupported_selection(select=[], exclude=None)

        # Test with None select and empty exclude
        worker._check_if_any_unsupported_selection(select=None, exclude=[])

        # Test with valid rules - should not raise errors
        worker._check_if_any_unsupported_selection(select=["name:test", "schema:test"], exclude=["exact:test"])

        # Test with invalid rule - should raise UsageError
        with pytest.raises(click.UsageError) as excinfo:
            worker._check_if_any_unsupported_selection(select=["invalid:test"], exclude=[])
        assert "Unsupported Selection found: invalid" in str(excinfo.value)
