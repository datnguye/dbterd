from typing import List

from dbterd.adapters.algos.meta import Table


def is_selected_table(
    table: Table, select_rules: List[str], resource_types=["model"], exclude_rules=[]
):
    selected = True
    if select_rules[0].startswith("schema"):
        schema = f"{table.database}.{table.schema}"
        selected = schema.startswith(select_rules[-1]) or table.schema.startswith(
            select_rules[-1]
        )
    else:
        selected = table.name.startswith(select_rules[-1])

    excluded = False
    if exclude_rules:
        excluded = table.name.startswith(exclude_rules)

    return selected and not excluded and table.resource_type in resource_types
