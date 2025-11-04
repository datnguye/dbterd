from typing import Optional, Union

from dbterd.adapters.algos._protocol import AlgorithmProtocol
from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.core.meta import Ref, SemanticEntity
from dbterd.core.registry import register_algorithm
from dbterd.helpers.log import logger
from dbterd.types import Manifest


@register_algorithm("semantic")
class SemanticAlgorithm(AlgorithmProtocol):
    """Semantic algorithm for detecting relationships based on dbt semantic entities.

    This algorithm analyzes dbt semantic models to extract relationships between
    tables based on foreign key and primary key entity definitions.
    """

    @property
    def name(self) -> str:
        """Return the algorithm name."""
        return "semantic"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "Detect relationships based on dbt semantic entities"

    def find_related_nodes_by_id(
        self,
        manifest: Union[Manifest, dict],
        node_unique_id: str,
        type: Optional[str] = None,
        **kwargs,
    ) -> list[str]:
        """Find FK/PK nodes which are linked to the given node.

        Args:
            manifest: dbt manifest data
            node_unique_id: Unique identifier of the node
            type: Optional node type filter (e.g., "metadata")
            **kwargs: Additional algorithm-specific parameters

        Returns:
            List of related node unique IDs
        """
        found_nodes = [node_unique_id]
        if type == "metadata":  # pragma: no cover
            return found_nodes  # not supported yet, returned input only

        entities = self._get_linked_semantic_entities(manifest=manifest)
        for foreign, primary in entities:
            if primary.model == node_unique_id:
                found_nodes.append(foreign.model)
            if foreign.model == node_unique_id:
                found_nodes.append(primary.model)

        return list(set(found_nodes))

    def get_relationships_from_metadata(self, data: list | None = None, **kwargs) -> list[Ref]:
        """Extract relationships from Metadata result list on Semantic Entities.

        Args:
            data: Metadata result list. Defaults to [].
            **kwargs: Additional options that might be passed from parent functions

        Returns:
            List of parsed relationship objects
        """
        if data is None:
            data = []
        entities = self._get_linked_semantic_entities_from_metadata(data=data)
        return self.get_unique_refs(
            refs=[
                Ref(
                    name=primary_entity.semantic_model,
                    table_map=(primary_entity.model, foreign_entity.model),
                    column_map=(
                        primary_entity.column_name,
                        foreign_entity.column_name,
                    ),
                    type=primary_entity.relationship_type,
                )
                for foreign_entity, primary_entity in entities
            ]
        )

    def get_relationships(self, manifest: Manifest, **kwargs) -> list[Ref]:
        """Extract relationships from dbt artifacts based on Semantic Entities.

        Args:
            manifest: dbt manifest data
            **kwargs: Additional options that might be passed from parent functions

        Returns:
            List of parsed relationship objects
        """
        entities = self._get_linked_semantic_entities(manifest=manifest)
        return self.get_unique_refs(
            refs=[
                Ref(
                    name=primary_entity.semantic_model,
                    table_map=(primary_entity.model, foreign_entity.model),
                    column_map=(
                        primary_entity.column_name,
                        foreign_entity.column_name,
                    ),
                    type=primary_entity.relationship_type,
                )
                for foreign_entity, primary_entity in entities
            ]
        )

    def _get_linked_semantic_entities_from_metadata(
        self, data: list | None = None
    ) -> list[tuple[SemanticEntity, SemanticEntity]]:
        """Get filtered list of Semantic Entities which are linked (Metadata).

        Args:
            data: Metadata result list. Defaults to [].

        Returns:
            List of (FK, PK) tuples
        """
        if data is None:
            data = []
        foreigns, primaries = self._get_semantic_entities_from_metadata(data=data)
        linked_entities = []
        for foreign_entity in foreigns:
            for primary_entity in primaries:
                if foreign_entity.entity_name == primary_entity.entity_name:
                    linked_entities.append((foreign_entity, primary_entity))
        return linked_entities

    def _get_linked_semantic_entities(self, manifest: Manifest) -> list[tuple[SemanticEntity, SemanticEntity]]:
        """Get filtered list of Semantic Entities which are linked.

        Args:
            manifest: dbt manifest data

        Returns:
            List of (FK, PK) tuples
        """
        foreigns, primaries = self._get_semantic_entities(manifest=manifest)
        linked_entities = []
        for foreign_entity in foreigns:
            for primary_entity in primaries:
                if foreign_entity.entity_name == primary_entity.entity_name:
                    linked_entities.append((foreign_entity, primary_entity))
        return linked_entities

    def _get_semantic_entities_from_metadata(
        self, data: list | None = None
    ) -> tuple[list[SemanticEntity], list[SemanticEntity]]:
        """Get all Semantic Entities (Metadata).

        Args:
            data: Metadata result list. Defaults to [].

        Returns:
            Tuple of (FK list, PK list)
        """
        if data is None:
            data = []
        fk_type = "foreign"
        pk_type = "primary"

        semantic_entities = []
        for data_item in data:
            for semantic_model in data_item.get("semanticModels", {}).get("edges", []):
                id = semantic_model.get("node", {}).get("uniqueId", "")
                meta = semantic_model.get("node", {}).get("meta", {}) or {}
                # currently only 1 parent with rs type of "model"
                model_id = semantic_model.get("node", {}).get("parents", {})[0].get("uniqueId", "")

                entities = semantic_model.get("node", {}).get("entities", [])
                for e in entities:
                    entity_name = e.get("name")
                    semantic_entities.append(
                        SemanticEntity(
                            semantic_model=id,
                            model=model_id,
                            entity_name=entity_name,
                            entity_type=e.get("type"),
                            column_name=e.get("expr") or entity_name,
                            relationship_type=(meta.get(TEST_META_RELATIONSHIP_TYPE, "") if meta else ""),
                        )
                    )

        return (
            [x for x in semantic_entities if x.entity_type == fk_type],
            [x for x in semantic_entities if x.entity_type == pk_type],
        )

    def _get_semantic_entities(self, manifest: Manifest) -> tuple[list[SemanticEntity], list[SemanticEntity]]:
        """Get all Semantic Entities.

        Args:
            manifest: dbt manifest data

        Returns:
            Tuple of (FK list, PK list)
        """
        fk_type = "foreign"
        pk_type = "primary"

        semantic_entities = []
        for x in self._get_semantic_nodes(manifest=manifest):
            semantic_node = manifest.semantic_models[x]
            for e in semantic_node.entities:
                if e.type.value in [pk_type, fk_type]:
                    semantic_entities.append(
                        SemanticEntity(
                            semantic_model=x,
                            model=semantic_node.depends_on.nodes[0],
                            entity_name=e.name,
                            entity_type=e.type.value,
                            column_name=e.expr or e.name,
                            relationship_type=semantic_node.config.meta.get(TEST_META_RELATIONSHIP_TYPE, ""),
                        )
                    )
            if semantic_node.primary_entity:
                semantic_entities.append(
                    SemanticEntity(
                        semantic_model=x,
                        model=semantic_node.depends_on.nodes[0],
                        entity_name=semantic_node.primary_entity,
                        entity_type=pk_type,
                        column_name=semantic_node.primary_entity,
                        relationship_type=semantic_node.config.meta.get(TEST_META_RELATIONSHIP_TYPE, ""),
                    )
                )

        return (
            [x for x in semantic_entities if x.entity_type == fk_type],
            [x for x in semantic_entities if x.entity_type == pk_type],
        )

    def _get_semantic_nodes(self, manifest: Manifest) -> list:
        """Extract the Semantic Models.

        Args:
            manifest: dbt manifest data

        Returns:
            List of Semantic Model IDs
        """
        if not hasattr(manifest, "semantic_models"):
            logger.warning(
                "No relationships will be captured since dbt version is NOT supported for the Semantic Models"
            )
            return []

        return [x for x in manifest.semantic_models if len(manifest.semantic_models[x].depends_on.nodes)]
