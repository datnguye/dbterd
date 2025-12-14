from typing import Optional

import yaml


# the C version is faster, but it doesn't always exist
try:
    from yaml import CDumper as Dumper, CLoader as Loader, CSafeLoader as SafeLoader
except ImportError:
    from yaml import Dumper, Loader, SafeLoader  # type: ignore  # noqa: F401


YAML_ERROR_MESSAGE = """
Syntax error near line {line_number}
------------------------------
{nice_error}
Raw Error:
------------------------------
{raw_error}
""".strip()


def line_no(i: int, line: str, width: int = 3) -> str:
    """Format a line with its line number.

    Args:
        i: Line number
        line: Line content
        width: Width for line number padding

    Returns:
        Formatted line with number prefix
    """
    line_number = str(i).ljust(width)
    return f"{line_number}| {line}"


def prefix_with_line_numbers(string: str, no_start: int, no_end: int) -> str:
    """Add line numbers as prefix to a range of lines.

    Args:
        string: Full text content
        no_start: Starting line index
        no_end: Ending line index

    Returns:
        Lines with number prefixes
    """
    line_list = string.split("\n")

    numbers = range(no_start, no_end)
    relevant_lines = line_list[no_start:no_end]

    return "\n".join([line_no(i + 1, line) for (i, line) in zip(numbers, relevant_lines)])


def contextualized_yaml_error(raw_contents: str, error: yaml.YAMLError) -> str:
    """Create a contextualized error message for YAML parsing errors.

    Args:
        raw_contents: Original YAML content
        error: YAML error with problem_mark attribute

    Returns:
        Formatted error message with context
    """
    mark = error.problem_mark

    min_line = max(mark.line - 3, 0)
    max_line = mark.line + 4

    nice_error = prefix_with_line_numbers(raw_contents, min_line, max_line)

    return YAML_ERROR_MESSAGE.format(line_number=mark.line + 1, nice_error=nice_error, raw_error=error)


def safe_load(contents: str) -> dict:
    """Safely load YAML content.

    Args:
        contents: YAML string content

    Returns:
        Parsed YAML as dictionary
    """
    return yaml.load(contents, Loader=SafeLoader)


class YamlParseError(Exception):
    """Custom exception for YAML parsing errors."""

    pass


def load_yaml_text(contents: str, path: Optional[str] = None) -> dict:
    """Load and parse YAML text content.

    Args:
        contents: YAML string content
        path: Optional path for error context

    Returns:
        Parsed YAML as dictionary

    Raises:
        YamlParseError: If YAML parsing fails
    """
    try:
        return safe_load(contents)
    except (yaml.scanner.ScannerError, yaml.YAMLError) as e:
        error = contextualized_yaml_error(contents, e) if hasattr(e, "problem_mark") else str(e)

        raise YamlParseError(error) from e
