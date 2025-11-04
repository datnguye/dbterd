import re
from typing import Optional

from dbterd.adapters.targets._protocol import TargetProtocol
from dbterd.core.registry import register_target
from dbterd.types import Catalog, Manifest


@register_target("mermaid")
class MermaidTarget(TargetProtocol):
    """Mermaid diagram target.

    This target generates Mermaid diagram output for visualizing dbt models.
    """

    @property
    def name(self) -> str:
        """Return the target format name."""
        return "mermaid"

    @property
    def file_extension(self) -> str:
        """Return the default file extension."""
        return ".mmd"

    def replace_column_name(self, column_name: str) -> str:
        """
        Replace column names containing special characters.
        To prevent mermaid from not being able to render column names that may contain special characters.

        Args:
            column_name (str): column name

        Returns:
            str: Column name with special characters substituted

        """
        return column_name.replace(" ", "-").replace(".", "__")

    def match_complex_column_type(self, column_type: str) -> Optional[str]:
        """
        Returns the root type from nested complex types.
        As an example, if the input is `Struct<field1 string, field2 string>`, return `Struct`.

        Args:
            column_type (str): column type

        Returns:
            Optional[str]: Returns root type if input type is nested complex type,
            otherwise returns `None` for primitive types

        """
        pattern = r"(\w+)<.*>"
        match = re.match(pattern, column_type)
        if match:
            return match.group(1)
        else:
            return None

    def replace_column_type(self, column_type: str) -> str:
        """
        If type of column contains special characters that cannot be drawn by mermaid,
        replace them with strings that can be drawn.
        If the type string contains a nested complex type, omit it to make it easier to read.

        Args:
            column_type (str): column type

        Returns:
            str: Type of column with special characters are substituted or omitted

        """
        # Some specific DWHs may have types that cannot be drawn in mermaid,
        # such as `Struct<first_name string, last_name string>`.
        # These types may be nested and can be very long, so omit them
        complex_column_type = self.match_complex_column_type(column_type)
        if complex_column_type:
            return f"{complex_column_type}[OMITTED]"
        else:
            return column_type.replace(" ", "-")

    def get_erd_text(self, manifest: Manifest, catalog: Catalog, **kwargs) -> str:
        """
        Get the Mermaid content from dbt artifacts.

        Args:
            manifest (dict): Manifest json
            catalog (dict): Catalog json

        Returns:
            str: Mermaid content

        """
        tables, relationships = self.get_erd_data(manifest=manifest, catalog=catalog, **kwargs)

        # Build Mermaid content
        # https://mermaid.js.org/syntax/entityRelationshipDiagram.html
        mermaid = "erDiagram\n"
        for table in tables:
            table_name = table.name.upper()
            table_label = f'["{table.label.upper()}"]' if hasattr(table, "label") and table.label else ""

            columns = "\n".join(
                [
                    f"    {self.replace_column_type(x.data_type)} {self.replace_column_name(x.name)}"
                    for x in table.columns
                ]
            )
            if kwargs.get("omit_columns", False):
                mermaid += f'  "{table_name}"{table_label} {{\n  }}\n'
            else:
                mermaid += f'  "{table_name}"{table_label} {{\n{columns}\n  }}\n'

        for rel in relationships:
            key_from = f'"{rel.table_map[1]}"'
            key_to = f'"{rel.table_map[0]}"'
            reference_text = self.replace_column_name(rel.column_map[0])
            if rel.column_map[0] != rel.column_map[1]:
                reference_text += f"--{self.replace_column_name(rel.column_map[1])}"
            if hasattr(rel, "relationship_label") and rel.relationship_label:
                reference_text = self.replace_column_name(rel.relationship_label)
            mermaid += f"  {key_from.upper()} {self.get_rel_symbol(rel.type)} {key_to.upper()}: {reference_text}\n"

        return mermaid

    def get_rel_symbol(self, relationship_type: str) -> str:
        """
        Get Mermaid relationship symbol.

        Args:
            relationship_type (str): relationship type

        Returns:
            str: Relation symbol supported in Mermaid

        """
        if relationship_type in ["01"]:
            return "}o--||"
        if relationship_type in ["11"]:
            return "||--||"
        if relationship_type in ["0n"]:
            return "}o--|{"
        if relationship_type in ["1n"]:
            return "||--|{"
        if relationship_type in ["nn"]:
            return "}|--|{"
        return "}|--||"  # n1
