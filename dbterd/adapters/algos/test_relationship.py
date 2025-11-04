from typing import Optional, Union

from dbterd.adapters.algos._protocol import AlgorithmProtocol
from dbterd.constants import TEST_META_IGNORE_IN_ERD, TEST_META_RELATIONSHIP_TYPE
from dbterd.core.meta import Ref
from dbterd.core.registry import register_algorithm
from dbterd.types import Manifest


@register_algorithm("test_relationship")
class TestRelationshipAlgorithm(AlgorithmProtocol):
    """Test relationship algorithm for detecting relationships based on dbt tests.

    This algorithm analyzes dbt relationship tests to extract foreign key
    relationships between tables.
    """

    @property
    def name(self) -> str:
        """Return the algorithm name."""
        return "test_relationship"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "Detect relationships based on dbt test configurations"

    def get_relationships_from_metadata(self, data: dict | None = None, **kwargs) -> list[Ref]:
        """Extract relationships from metadata based on test relationships.

        Args:
            data: Metadata dictionary
            **kwargs: Additional algorithm-specific parameters

        Returns:
            List of parsed relationship objects
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
                                (
                                    test_metadata_kwargs.get(rule.get("c_to"))
                                    or "_and_".join(test_metadata_kwargs.get(f"{rule.get('c_to')}s", "unknown"))
                                )
                                .replace('"', "")
                                .lower(),
                                (
                                    test_metadata_kwargs.get("columnName")
                                    or test_metadata_kwargs.get(rule.get("c_from"))
                                    or "_and_".join(test_metadata_kwargs.get(f"{rule.get('c_from')}s", "unknown"))
                                )
                                .replace('"', "")
                                .lower(),
                            ],
                            type=self.get_relationship_type(test_meta.get(TEST_META_RELATIONSHIP_TYPE, "")),
                            relationship_label=test_meta.get("relationship_label"),
                        )
                    )

        return self.get_unique_refs(refs=refs)

    def get_relationships(self, manifest: Manifest, **kwargs) -> list[Ref]:
        """Extract relationships from dbt artifacts based on test relationships.

        Args:
            manifest: dbt manifest data
            **kwargs: Additional algorithm-specific parameters

        Returns:
            List of parsed relationship objects
        """
        rule = self.get_algo_rule(**kwargs)
        refs = [
            Ref(
                name=x,
                table_map=self.get_table_map(test_node=manifest.nodes[x], **kwargs),
                column_map=[
                    str(
                        manifest.nodes[x].test_metadata.kwargs.get(rule.get("c_to"))
                        or "_and_".join(manifest.nodes[x].test_metadata.kwargs.get(f"{rule.get('c_to')}s", "unknown"))
                    )
                    .replace('"', "")
                    .lower(),
                    str(
                        manifest.nodes[x].test_metadata.kwargs.get("column_name")
                        or manifest.nodes[x].test_metadata.kwargs.get(rule.get("c_from"))
                        or "_and_".join(manifest.nodes[x].test_metadata.kwargs.get(f"{rule.get('c_from')}s", "unknown"))
                    )
                    .replace('"', "")
                    .lower(),
                ],
                type=self.get_relationship_type(manifest.nodes[x].meta.get(TEST_META_RELATIONSHIP_TYPE, "")),
                relationship_label=manifest.nodes[x].meta.get("relationship_label"),
            )
            for x in self.get_test_nodes_by_rule_name(manifest=manifest, rule_name=rule.get("name").lower())
        ]

        return self.get_unique_refs(refs=refs)

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """Find the FK models which are related to the input model ID inclusively.

        Given the manifest data of dbt project.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest node unique ID
            type: Manifest type (local file or metadata). Defaults to None.
            **kwargs: Additional options that might be passed from parent functions

        Returns:
            List[str]: Manifest nodes' unique ID
        """
        found_nodes = [node_unique_id]
        if type == "metadata":
            return found_nodes  # not supported yet, returned input only

        rule = self.get_algo_rule(**kwargs)
        test_nodes = self.get_test_nodes_by_rule_name(manifest=manifest, rule_name=rule.get("name").lower())

        for test_node in test_nodes:
            nodes = manifest.nodes[test_node].depends_on.nodes or []
            if node_unique_id in nodes:
                found_nodes.extend(nodes)

        return list(set(found_nodes))
