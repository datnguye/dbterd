import json

from dbterd.adapters.targets._protocol import TargetProtocol
from dbterd.core.registry import register_target
from dbterd.types import Catalog, Manifest


@register_target("dbml")
class DBMLTarget(TargetProtocol):
    """DBML (Database Markup Language) target.

    This target generates DBML (Database Markup Language) output for visualizing dbt models.
    """

    @property
    def name(self) -> str:
        """Return the target format name."""
        return "dbml"

    @property
    def file_extension(self) -> str:
        """Return the default file extension."""
        return ".dbml"

    def get_erd_text(self, manifest: Manifest, catalog: Catalog, **kwargs) -> str:
        """
        Get the DBML content from dbt artifacts.

        Args:
            manifest (dict): Manifest json
            catalog (dict): Catalog json

        Returns:
            str: DBML content

        """
        tables, relationships = self.get_erd_data(manifest=manifest, catalog=catalog, **kwargs)

        # Build DBML content
        dbml = "//Tables (based on the selection criteria)\n"
        quote = "" if kwargs.get("omit_entity_name_quotes") else '"'
        for table in tables:
            dbml += f"//--configured at schema: {table.database}.{table.schema}\n"
            dbml += "Table {quote}{table}{quote} {{\n{columns}\n\n  Note: {table_note}\n}}\n".format(
                quote=quote,
                table=table.name,
                columns="\n".join(
                    [
                        str.format(
                            '  "{0}" "{1}"{2}',
                            x.name,
                            x.data_type,
                            (str.format(" [note: {0}]", json.dumps(x.description)) if x.description else ""),
                        )
                        for x in table.columns
                    ]
                ),
                table_note=json.dumps(table.description),
            )

        dbml += "//Refs (based on the DBT Relationship Tests)\n"
        for rel in relationships:
            key_from = f'{quote}{rel.table_map[1]}{quote}."{rel.column_map[1]}"'
            key_to = f'{quote}{rel.table_map[0]}{quote}."{rel.column_map[0]}"'
            dbml += f"Ref: {key_from} {self.get_rel_symbol(rel.type)} {key_to}\n"
        return dbml

    def get_rel_symbol(self, relationship_type: str) -> str:
        """
        Get DBML relationship symbol.

        Args:
            relationship_type (str): relationship type

        Returns:
            str: Relation symbol supported in DBML

        """
        if relationship_type in ["01", "11"]:
            return "-"
        if relationship_type in ["0n", "1n"]:
            return "<"
        if relationship_type in ["nn"]:
            return "<>"
        return ">"  # n1
