from typing import List

from dbterd.adapters.algos.meta import Table


def is_selected_table(
    table: Table,
    select_rules: List[str] = [],
    exclude_rules: List[str] = [],
    resource_types: List[str] = ["model"],
):
    """Check if Table is selected with defined selection criteria

    Args:
        table (Table): Table object
        select_rules (List[str]): Selection rules. Defaults to [].
        exclude_rules (List[str], optional): Exclusion rules. Defaults to [].
        resource_types (List[str], optional): Selected resource types. Defaults to [].

    Returns:
        bool: True if Table is selected. False if Tables is excluded
    """
    selected = True
    if select_rules:
        select_rule = select_rules[0].lower().split(":")
        if len(select_rule) > 1 and select_rule[0].startswith("schema"):
            schema = f"{table.database}.{table.schema}"
            selected = schema.startswith(select_rule[1]) or table.schema.startswith(
                select_rule[1]
            )
        else:
            selected = table.name.startswith(select_rule[0])

    if resource_types:
        selected = selected and table.resource_type in resource_types

    excluded = False
    if exclude_rules:
        exclude_rule = exclude_rules[0]
        excluded = table.name.startswith(exclude_rule)

    return selected and not excluded
