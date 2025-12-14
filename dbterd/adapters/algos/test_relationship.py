"""Test relationship algorithm adapter for dbterd.

This module extracts tables and relationships from dbt artifacts
using dbt's relationship tests to determine connections.
"""

from typing import Optional, Union

import click

from dbterd.constants import (
    DEFAULT_ALGO_RULE,
    TEST_META_IGNORE_IN_ERD,
    TEST_META_RELATIONSHIP_TYPE,
)
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


# Constants
MAX_TEST_PARENTS = 2


def _extract_column_name(kwargs: dict, rule_key: str) -> str:
    """Extract and normalize column name from test metadata kwargs.

    Args:
        kwargs: Test metadata kwargs dictionary
        rule_key: Rule key to look up (e.g., 'c_to', 'c_from')

    Returns:
        Normalized lowercase column name
    """
    column = kwargs.get(rule_key) or "_and_".join(kwargs.get(f"{rule_key}s", ["unknown"]))
    return str(column).replace('"', "").lower()


@register_algo("test_relationship", description="Detect relationships via dbt tests")
class TestRelationshipAlgo(BaseAlgoAdapter):
    """Algorithm adapter using dbt relationship tests.

    Extracts relationships from dbt's built-in relationship tests
    to determine table connections in the ERD.
    """

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        # Parse Table
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        # Parse Ref
        relationships = self.get_relationships(manifest=manifest, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        # Fulfill columns in Tables (due to `select *`)
        tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from dbt Cloud metadata API response."""
        # Parse Table
        tables = self.get_tables_from_metadata(data=data, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        # Parse Ref
        relationships = self.get_relationships_from_metadata(data=data, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """Find FK models related to the input model ID.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type (local file or metadata)
            **kwargs: Additional options

        Returns:
            List of manifest node unique IDs

        """
        found_nodes = [node_unique_id]
        if type == "metadata":
            return found_nodes  # not supported yet, return input only

        rule = self.get_algo_rule(**kwargs)
        test_nodes = self.get_test_nodes_by_rule_name(manifest=manifest, rule_name=rule.get("name").lower())

        for test_node in test_nodes:
            nodes = manifest.nodes[test_node].depends_on.nodes or []
            if node_unique_id in nodes:
                found_nodes.extend(nodes)

        return list(set(found_nodes))

    def get_relationships(self, manifest: Manifest, **kwargs) -> list[Ref]:
        """Extract relationships from dbt artifacts based on test relationship.

        Args:
            manifest (dict): Manifest json
            **kwargs: Additional options including:
                rule_name (str): Custom rule name for the algorithm
                rule_prefix (str): Prefix for the rule
                entity_name_format (str): Format for entity names

        Returns:
            List[Ref]: List of parsed relationship

        """
        rule = self.get_algo_rule(**kwargs)
        refs = [
            Ref(
                name=x,
                table_map=self.get_table_map(test_node=manifest.nodes[x], **kwargs),
                column_map=[
                    _extract_column_name(manifest.nodes[x].test_metadata.kwargs, rule.get("c_to")),
                    (
                        str(manifest.nodes[x].test_metadata.kwargs.get("column_name") or "").replace('"', "").lower()
                        or _extract_column_name(manifest.nodes[x].test_metadata.kwargs, rule.get("c_from"))
                    ),
                ],
                type=self.get_relationship_type(manifest.nodes[x].meta.get(TEST_META_RELATIONSHIP_TYPE, "")),
                relationship_label=manifest.nodes[x].meta.get("relationship_label"),
            )
            for x in self.get_test_nodes_by_rule_name(manifest=manifest, rule_name=rule.get("name").lower())
        ]

        return self.get_unique_refs(refs=refs)

    def get_relationships_from_metadata(self, data=None, **kwargs) -> list[Ref]:
        """Extract relationships from Metadata result list on test relationship.

        Args:
            data (list, optional): Metadata result list. Defaults to [].
            **kwargs: Additional options including:
                rule_name (str): Custom rule name for the algorithm
                rule_prefix (str): Prefix for the rule

        Returns:
            list[Ref]: List of parsed relationship

        """
        if data is None:
            data = []
        refs = []
        rule = self.get_algo_rule(**kwargs)

        for data_item in data:
            for test in data_item.get("tests", {}).get("edges", []):
                test_id = test.get("node", {}).get("uniqueId", "")
                test_meta = test.get("node", {}).get("meta", {})
                if (
                    test_id.startswith("test")
                    and rule.get("name").lower() in test_id.lower()
                    and test_meta is not None
                    and test_meta.get(TEST_META_IGNORE_IN_ERD, "0") == "0"
                ):
                    test_metadata_kwargs = test.get("node", {}).get("testMetadata", {}).get("kwargs", {})
                    refs.append(
                        Ref(
                            name=test_id,
                            table_map=self.get_table_map_from_metadata(test_node=test, **kwargs),
                            column_map=[
                                _extract_column_name(test_metadata_kwargs, rule.get("c_to")),
                                (
                                    str(test_metadata_kwargs.get("columnName") or "").replace('"', "").lower()
                                    or _extract_column_name(test_metadata_kwargs, rule.get("c_from"))
                                ),
                            ],
                            type=self.get_relationship_type(test_meta.get(TEST_META_RELATIONSHIP_TYPE, "")),
                            relationship_label=test_meta.get("relationship_label"),
                        )
                    )

        return self.get_unique_refs(refs=refs)

    def get_algo_rule(self, **kwargs) -> dict[str, str]:
        """Extract rule from the --algo option.

        Args:
            **kwargs: Additional options including:
                algo (str): Algorithm name and optional rules

        Details:
            Samples for algo parameter:
            - test_relationship
            - test_relationship:(name:relationship|c_from:column_name|c_to:field)
            - test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)
            - test_relationship:(
                name:foreign_key|
                c_from:fk_column_name|
                c_to:pk_column_name|
                t_to:pk_table_name
            )

        Returns:
            dict: Rule object (
                name [default 'relationship', use contains],
                c_from [default 'column_name'],
                c_to [default 'field'],
                t_to [default 'to']
            )

        """
        algo_parts = (kwargs.get("algo") or "").replace(" ", "").split(":", 1)
        rules, _ = (
            algo_parts[1] if len(algo_parts) > 1 else DEFAULT_ALGO_RULE,
            algo_parts[0],
        )
        rules = rules[1:-1]  # remove brackets
        rules = dict(arg.split(":") for arg in rules.split("|"))
        return rules

    def get_test_nodes_by_rule_name(self, manifest: Manifest, rule_name: str) -> list:
        """Get manifest nodes given the algo rule name.

        Default algo rule name is `relationship`,
        see `get_algo_rule` function for more details.

        Args:
            rule_name (str): Rule name
            manifest (Manifest): Manifest data

        Returns:
            List: List of manifest nodes

        """
        return [
            x
            for x in manifest.nodes
            if (
                x.startswith("test")
                and rule_name in x.lower()
                and manifest.nodes[x].meta.get(TEST_META_IGNORE_IN_ERD, "0") == "0"
            )
        ]

    def get_table_map(self, test_node, **kwargs) -> list[str]:
        """Get the table map with order of [to, from] guaranteed.

        Args:
            test_node (dict): Manifest Test node
            **kwargs: Additional options passed from parent functions

        Returns:
            list: [to model, from model]

        """
        map = test_node.depends_on.nodes or []

        # Recursive relation case
        # `from` and `to` will be identical and `test_node.depends_on.nodes` will contain only one element
        if len(map) == 1:
            return [map[0], map[0]]

        rule = self.get_algo_rule(**kwargs)
        to_model = str(test_node.test_metadata.kwargs.get(rule.get("t_to", "to"), {}))
        if f'("{map[1].split(".")[-1]}")'.lower() in to_model.replace("'", '"').lower():
            return [map[1], map[0]]

        return map

    def get_table_map_from_metadata(self, test_node, **kwargs) -> list[str]:
        """Get the table map with order of [to, from] guaranteed.

        (for Metadata)

        Args:
            test_node (dict): Metadata test node
            **kwargs: Additional options passed from parent functions

        Raises:
            click.BadParameter: A Ref must have 2 parents

        Returns:
            list: [to model, from model]

        """
        rule = self.get_algo_rule(**kwargs)

        test_parents = []
        for parent in test_node.get("node", {}).get("parents", []):
            parent_id = parent.get("uniqueId", "")
            if parent_id.split(".")[0] in kwargs.get("resource_type", []):
                test_parents.append(parent_id)

        if len(test_parents) == 0:
            return ["", ""]  # return dummies - need to be excluded manually

        if len(test_parents) == 1:
            return [test_parents[0], test_parents[0]]  # self FK

        if len(test_parents) > MAX_TEST_PARENTS:
            logger.debug(f"Collected test parents: {test_parents}")
            raise click.BadParameter("Relationship test unexpectedly doesn't have >2 parents")

        test_metadata_to = (
            test_node.get("node", {}).get("testMetadata", {}).get("kwargs", {}).get(rule.get("t_to", "to"), "")
        )

        first_test_parent_parts = test_parents[0].split(".")
        first_test_parent_resource_type = (
            "ref" if first_test_parent_parts[0] != "source" else first_test_parent_parts[0]
        )
        to_model_possible_values = [
            f"{first_test_parent_resource_type}('{first_test_parent_parts[2]}', '{first_test_parent_parts[-1]}')",
            f"{first_test_parent_resource_type}('{first_test_parent_parts[-1]}')",
            f'{first_test_parent_resource_type}("{first_test_parent_parts[2]}", "{first_test_parent_parts[-1]}")',
            f'{first_test_parent_resource_type}("{first_test_parent_parts[-1]}")',
        ]
        if test_metadata_to in to_model_possible_values:
            return test_parents

        return list(reversed(test_parents))

    def get_relationship_type(self, meta: str) -> str:
        """Get short form of the relationship type configured in test meta.

        Args:
            meta (str): meta value

        Returns:
            str: |
                Short relationship type. Accepted values: '0n','01','11','nn','n1' and '1n'.
                And `1n` is default/fallback value

        """
        if meta.lower() == "zero-to-many":
            return "0n"
        if meta.lower() == "zero-to-one":
            return "01"
        if meta.lower() == "one-to-one":
            return "11"
        if meta.lower() == "many-to-many":
            return "nn"
        if meta.lower() == "one-to-many":
            return "1n"
        return "n1"  # "many-to-one"
