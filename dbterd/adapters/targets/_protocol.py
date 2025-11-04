from abc import ABC, abstractmethod
import copy

from dbterd.core.filter import is_selected_table
from dbterd.core.meta import Column
from dbterd.types import Catalog, Manifest


class TargetProtocol(ABC):
    """Base class for all target formatters.

    This class defines the interface that all target implementations
    must follow to be compatible with the registry system.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Target format name.

        Returns:
            str: Unique name for this target format
        """
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Default file extension for this format.

        Returns:
            str: File extension (e.g., '.dbml', '.mmd')
        """
        ...

    def run(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[str, str]:
        """Generate target format output.

        Args:
            manifest: dbt manifest data
            catalog: dbt catalog data
            **kwargs: Additional target-specific parameters

        Returns:
            Tuple containing:
                - Output file name
                - Generated content
        """
        output_file_name = kwargs.get("output_file_name") or f"output{self.file_extension}"
        return (output_file_name, self.get_erd_text(manifest, catalog, **kwargs))

    def get_erd_data(self, manifest: Manifest, catalog: Catalog, **kwargs):
        """Get tables and relationships from dbt artifacts using algorithm.

        Args:
            manifest: dbt manifest data
            catalog: dbt catalog data
            **kwargs: Additional parameters including 'algo'

        Returns:
            tuple: (tables, relationships)
        """
        algo = self.get_algorithm(algo_name=kwargs["algo"])
        tables, relationships = algo.parse(manifest=manifest, catalog=catalog, **kwargs)

        # Apply filtering based on selection criteria
        # (This handles cases where parse() is mocked in tests)
        tables = [
            table
            for table in tables
            if is_selected_table(
                table=table,
                select_rules=kwargs.get("select") or [],
                resource_types=kwargs.get("resource_type", []),
                exclude_rules=kwargs.get("exclude") or [],
            )
        ]

        # Filter relationships to only include those between tables that exist
        table_names = {table.name for table in tables}
        relationships = [
            rel for rel in relationships if rel.table_map[0] in table_names and rel.table_map[1] in table_names
        ]

        # Enrich tables with missing columns from relationships
        # (This handles cases where parse() is mocked in tests)
        copied_tables = copy.deepcopy(tables)
        for relationship in relationships:
            for table in copied_tables:
                table_columns = [x.name.lower() for x in table.columns]
                if table.name == relationship.table_map[0] and relationship.column_map[0].lower() not in table_columns:
                    table.columns.append(Column(name=relationship.column_map[0]))
                if table.name == relationship.table_map[1] and relationship.column_map[1].lower() not in table_columns:
                    table.columns.append(Column(name=relationship.column_map[1]))

        return (copied_tables, relationships)

    @abstractmethod
    def get_erd_text(self, manifest: Manifest, catalog: Catalog, **kwargs) -> str:
        """Parse dbt artifacts and generate target format content.

        This method should call get_erd_data() to retrieve tables and relationships,
        then format them according to the target format.

        Args:
            manifest: dbt manifest data
            catalog: dbt catalog data
            **kwargs: Additional target-specific parameters including 'algo'

        Returns:
            str: Generated content in target format
        """
        ...

    def get_algorithm(self, algo_name: str):
        """Get algorithm parser from registry.

        Args:
            algo_name: Name of the algorithm to retrieve

        Returns:
            Algorithm instance
        """
        from dbterd.core.registry.manager import registry  # noqa: PLC0415

        return registry.get_parser(name=algo_name)
