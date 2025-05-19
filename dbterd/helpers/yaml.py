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


def line_no(i, line, width=3):
    line_number = str(i).ljust(width)
    return f"{line_number}| {line}"


def prefix_with_line_numbers(string, no_start, no_end):
    line_list = string.split("\n")

    numbers = range(no_start, no_end)
    relevant_lines = line_list[no_start:no_end]

    return "\n".join([line_no(i + 1, line) for (i, line) in zip(numbers, relevant_lines)])


def contextualized_yaml_error(raw_contents, error):
    mark = error.problem_mark

    min_line = max(mark.line - 3, 0)
    max_line = mark.line + 4

    nice_error = prefix_with_line_numbers(raw_contents, min_line, max_line)

    return YAML_ERROR_MESSAGE.format(line_number=mark.line + 1, nice_error=nice_error, raw_error=error)


def safe_load(contents):
    return yaml.load(contents, Loader=SafeLoader)


class YamlParseError(Exception):
    """Custom exception for YAML parsing errors."""

    pass


def load_yaml_text(contents, path=None):
    try:
        return safe_load(contents)
    except (yaml.scanner.ScannerError, yaml.YAMLError) as e:
        error = contextualized_yaml_error(contents, e) if hasattr(e, "problem_mark") else str(e)

        raise YamlParseError(error) from e
