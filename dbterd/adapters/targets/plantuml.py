from dbterd.adapters.targets._protocol import TargetProtocol
from dbterd.core.registry import register_target
from dbterd.types import Catalog, Manifest


@register_target("plantuml")
class PlantUMLTarget(TargetProtocol):
    """PlantUML diagram target.

    This target generates PlantUML diagram output for visualizing dbt models.
    """

    @property
    def name(self) -> str:
        """Return the target format name."""
        return "plantuml"

    @property
    def file_extension(self) -> str:
        """Return the default file extension."""
        return ".plantuml"

    def get_erd_text(self, manifest: Manifest, catalog: Catalog, **kwargs) -> str:
        """
        Get the PlantUML content from dbt artifacts.

        Args:
            manifest (dict): Manifest json
            catalog (dict): Catalog json

        Returns:
            str: PlantUML content

        """
        tables, relationships = self.get_erd_data(manifest=manifest, catalog=catalog, **kwargs)

        # Build PlantUML content
        # https://plantuml.com/ie-diagram, https://www.plantuml.com/plantuml/uml
        plantuml = "@startuml\n"
        for table in tables:
            plantuml += 'entity "{table}" {{\n{columns}\n  }}\n'.format(
                table=table.name,
                columns="\n".join([f"    {x.name} : {x.data_type}" for x in table.columns]),
            )

        for rel in relationships:
            key_from = f'"{rel.table_map[1]}"'
            key_to = f'"{rel.table_map[0]}"'
            # NOTE: plant uml doesn't have columns defined in the connector
            new_rel = f"  {key_from} {self.get_rel_symbol(rel.type)} {key_to}\n"
            if new_rel not in plantuml:
                plantuml += new_rel

        plantuml += "@enduml"

        return plantuml

    def get_rel_symbol(self, relationship_type: str) -> str:
        """
        Get PlantUML relationship symbol.

        Args:
            relationship_type (str): relationship type

        Returns:
            str: Relation symbol supported in PlantUML

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
