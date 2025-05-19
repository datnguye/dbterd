"""Tests for the yaml helpers module."""

import importlib
import sys
from unittest import mock

import pytest
import yaml

from dbterd.helpers import yaml as yaml_helper


def test_line_no():
    """Test line_no function formats line numbers correctly."""
    assert yaml_helper.line_no(1, "test", 3) == "1  | test"
    assert yaml_helper.line_no(10, "test", 3) == "10 | test"
    assert yaml_helper.line_no(100, "test", 3) == "100| test"

    # Custom width
    assert yaml_helper.line_no(1, "test", 5) == "1    | test"


def test_prefix_with_line_numbers():
    """Test prefix_with_line_numbers adds line numbers to a string."""
    content = "line1\nline2\nline3\nline4\nline5"

    # Get lines 2-4 (0-indexed)
    result = yaml_helper.prefix_with_line_numbers(content, 1, 4)
    expected = "2  | line2\n3  | line3\n4  | line4"

    assert result == expected


def test_contextualized_yaml_error():
    """Test contextualized_yaml_error provides context around YAML errors."""
    content = "key1: value1\nkey2: value2\nkey3: : invalid\nkey4: value4\nkey5: value5"

    # Create a mock error with a problem_mark
    error = yaml.scanner.ScannerError("test error")
    error.problem_mark = type(
        "obj",
        (object,),
        {
            "line": 2,  # 0-indexed, points to "key3: : invalid"
            "column": 7,
        },
    )

    result = yaml_helper.contextualized_yaml_error(content, error)

    # Verify the result contains the expected context
    assert "line 3" in result  # 1-indexed in output
    assert "key2: value2" in result  # Line before
    assert "key3: : invalid" in result  # Error line
    assert "key4: value4" in result  # Line after


def test_safe_load():
    """Test safe_load loads YAML safely."""
    content = "key: value\nlist:\n  - item1\n  - item2"
    result = yaml_helper.safe_load(content)

    expected = {"key": "value", "list": ["item1", "item2"]}

    assert result == expected


def test_load_yaml_text_valid():
    """Test load_yaml_text with valid YAML."""
    content = "key: value\nlist:\n  - item1\n  - item2"
    result = yaml_helper.load_yaml_text(content)

    expected = {"key": "value", "list": ["item1", "item2"]}

    assert result == expected


def test_load_yaml_text_invalid():
    """Test load_yaml_text raises error for invalid YAML."""
    content = "key: value\nkey: : invalid"

    with pytest.raises(yaml_helper.YamlParseError) as excinfo:
        yaml_helper.load_yaml_text(content)

    # Check error contains contextualized information
    assert "line" in str(excinfo.value)


def test_load_yaml_text_other_error():
    """Test load_yaml_text with an error that doesn't have problem_mark."""

    class MockError(yaml.YAMLError):
        """Mock error without problem_mark."""

        pass

    # Create a custom error that doesn't have problem_mark
    error = MockError("Custom error")

    # Mock safe_load to raise our custom error
    original_safe_load = yaml_helper.safe_load

    def mock_safe_load(contents):
        raise error

    yaml_helper.safe_load = mock_safe_load

    try:
        with pytest.raises(yaml_helper.YamlParseError) as excinfo:
            yaml_helper.load_yaml_text("content")

        # Should just convert the error to string
        assert "Custom error" in str(excinfo.value)
    finally:
        # Restore original function
        yaml_helper.safe_load = original_safe_load


def test_yaml_import_options():
    """Test both YAML import paths."""
    # Save original module
    orig_yaml = sys.modules["yaml"]

    try:
        # Test the case where C versions are available
        mock_c_yaml = mock.MagicMock()
        mock_c_yaml.CDumper = mock.MagicMock()
        mock_c_yaml.CLoader = mock.MagicMock()
        mock_c_yaml.CSafeLoader = mock.MagicMock()
        sys.modules["yaml"] = mock_c_yaml

        # Reimport to trigger the imports
        importlib.reload(yaml_helper)

        # Test the fallback case
        mock_py_yaml = mock.MagicMock()
        mock_py_yaml.CDumper = None
        # Raise ImportError when CDumper accessed
        type(mock_py_yaml).CDumper = mock.PropertyMock(side_effect=ImportError)
        mock_py_yaml.Dumper = mock.MagicMock()
        mock_py_yaml.Loader = mock.MagicMock()
        mock_py_yaml.SafeLoader = mock.MagicMock()
        sys.modules["yaml"] = mock_py_yaml

        # Reimport to trigger the fallback imports
        importlib.reload(yaml_helper)

        # Verification is that no exceptions were raised
        assert True
    finally:
        # Restore original module
        sys.modules["yaml"] = orig_yaml
        importlib.reload(yaml_helper)
