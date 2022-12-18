from dbterd.adapters.targets.dbml.engine.meta import Ref, Table, Column
from sql_metadata import Parser


def parse(**kwargs):
    manifest = kwargs.get("manifest")

    tables = get_tables(manifest)
    relationships = get_relationships(manifest)

    dbml = ""
    for table in tables:
        dbml += """Table \"{table}\"{{
            {columns}
        }}\n
        """.format(
            table=table.name,
            columns="\n".join([f'"{x.name}" {x.data_type}' for x in table.columns]),
        )
    for rel in relationships:
        dbml += f"""Ref: \"{rel.table_map[1]}\".\"{rel.column_map[1]}\" > \"{rel.table_map[0]}\".\"{rel.column_map[0]}\"
        """

    return dbml


def get_tables(manifest):
    tables = [
        Table(name=x, raw_sql=manifest.nodes[x].compiled_sql, columns=[])
        for x in manifest.nodes
        if x.startswith("model")
    ]
    for table in tables:
        parser = Parser(table.raw_sql)
        columns = parser.columns_aliases_names
        for column in columns:
            table.columns.append(
                Column(
                    name=column,
                )
            )

    return tables


def get_relationships(manifest):
    return [
        Ref(
            name=x,
            table_map=manifest.parent_map[x],
            column_map=[
                manifest.nodes[x].test_metadata.kwargs.get("field", "unknown"),
                manifest.nodes[x].test_metadata.kwargs.get("column_name", "unknown"),
            ],
        )
        for x in manifest.nodes
        if x.startswith("test") and "relationship" in x.lower()
    ]
