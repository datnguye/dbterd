"""Semantic algorithm adapter for dbterd.

This module extracts tables and relationships from dbt artifacts
using dbt's Semantic Layer entities to determine connections.
"""

from typing import Optional, Union

from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, SemanticEntity, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


@register_algo("semantic", description="Detect relationships via Semantic Layer entities")
class SemanticAlgo(BaseAlgoAdapter):
    """Algorithm adapter using dbt Semantic Layer entities.

    Extracts relationships from dbt's Semantic Layer entity definitions
    (primary/foreign entities) to determine table connections.
    """

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        # Parse Table
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        # Parse Ref
        relationships = self.get_relationships(manifest=manifest)
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
        data_list = data if isinstance(data, list) else [data]

        # Parse Table
        tables = self.get_tables_from_metadata(data=data_list, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        # Parse Ref
        relationships = self.get_relationships_from_metadata(data=data_list)
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
        """Find FK/PK nodes linked to the given node.

        Args:
            manifest: Manifest data
            node_unique_id: Manifest model node unique ID
            type: Manifest type (local file or metadata)
            **kwargs: Additional options

        Returns:
            List of manifest node unique IDs

        """
        found_nodes = [node_unique_id]
        if type == "metadata":  # pragma: no cover
            return found_nodes  # not supported yet, return input only

        entities = self.get_linked_semantic_entities(manifest=manifest)
        for foreign, primary in entities:
            if primary.model == node_unique_id:
                found_nodes.append(foreign.model)
            if foreign.model == node_unique_id:
                found_nodes.append(primary.model)

        return list(set(found_nodes))

    def get_semantic_nodes(self, manifest: Manifest) -> list:
        """Extract the Semantic Models.

        Args:
            manifest: Manifest data

        Returns:
            List of Semantic Models

        """
        if not hasattr(manifest, "semantic_models"):
            logger.warning(
                "No relationships will be captured since dbt version is NOT supported for the Semantic Models"
            )
            return []

        return [x for x in manifest.semantic_models if len(manifest.semantic_models[x].depends_on.nodes)]

    def get_semantic_entities(
        self,
        manifest: Manifest,
    ) -> tuple[list[SemanticEntity], list[SemanticEntity]]:
        """Get all Semantic Entities.

        Args:
            manifest: Manifest data

        Returns:
            Tuple of (FK list, PK list)

        """
        fk_type = "foreign"
        pk_type = "primary"

        semantic_entities = []
        for x in self.get_semantic_nodes(manifest=manifest):
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

    def get_semantic_entities_from_metadata(
        self,
        data: list,
    ) -> tuple[list[SemanticEntity], list[SemanticEntity]]:
        """Get all Semantic Entities from metadata.

        Args:
            data: Metadata result list

        Returns:
            Tuple of (FK list, PK list)

        """
        fk_type = "foreign"
        pk_type = "primary"

        semantic_entities = []
        for data_item in data or []:
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

    def get_linked_semantic_entities(
        self,
        manifest: Manifest,
    ) -> list[tuple[SemanticEntity, SemanticEntity]]:
        """Get filtered list of Semantic Entities which are linked.

        Args:
            manifest: Manifest data

        Returns:
            List of (FK, PK) entity tuples

        """
        foreigns, primaries = self.get_semantic_entities(manifest=manifest)
        linked_entities = []
        for foreign_entity in foreigns:
            for primary_entity in primaries:
                if foreign_entity.entity_name == primary_entity.entity_name:
                    linked_entities.append((foreign_entity, primary_entity))
        return linked_entities

    def get_linked_semantic_entities_from_metadata(
        self,
        data: list,
    ) -> list[tuple[SemanticEntity, SemanticEntity]]:
        """Get filtered list of Semantic Entities which are linked (metadata).

        Args:
            data: Metadata result list

        Returns:
            List of (FK, PK) entity tuples

        """
        foreigns, primaries = self.get_semantic_entities_from_metadata(data=data)
        linked_entities = []
        for foreign_entity in foreigns:
            for primary_entity in primaries:
                if foreign_entity.entity_name == primary_entity.entity_name:
                    linked_entities.append((foreign_entity, primary_entity))
        return linked_entities

    def get_relationships(self, manifest: Manifest) -> list[Ref]:
        """Extract relationships from dbt artifacts based on Semantic Entities.

        Args:
            manifest: Manifest data

        Returns:
            List of parsed relationships

        """
        entities = self.get_linked_semantic_entities(manifest=manifest)
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

    def get_relationships_from_metadata(self, data: list) -> list[Ref]:
        """Extract relationships from Metadata result list on Semantic Entities.

        Args:
            data: Metadata result list

        Returns:
            List of parsed relationships

        """
        entities = self.get_linked_semantic_entities_from_metadata(data=data)
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
