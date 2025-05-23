from importlib import import_module


def load_target(name: str):
    """
    Import the target extension dynamically.

    Args:
        name (str): Target name e.g. dbml, mermaid

    Raises:
        Exception: Target not found

    Returns:
        ModuleType: Imported module

    """
    try:
        return import_module(name=f".{name}", package="dbterd.adapters.targets")
    except ModuleNotFoundError as exc:
        if exc.name == "dbterd.adapters.targets." + name:
            raise Exception(f"Could not find adapter target type {name}!") from exc
        raise  # pragma: no cover


def load_algo(name: str):
    """
    Import the algo extension dynamically.

    Args:
        name (str): Algo name e.g. test_relationship

    Raises:
        Exception: Algo not found

    Returns:
        ModuleType: Imported module

    """
    module_name = name.split(":")[0]
    try:
        return import_module(name=f".{module_name}", package="dbterd.adapters.algos")
    except ModuleNotFoundError as exc:
        if exc.name == "dbterd.adapters.algos." + module_name:
            raise Exception(f"Could not find adapter algo {module_name}!") from exc
        raise  # pragma: no cover
