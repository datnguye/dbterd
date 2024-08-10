from typing import List, Tuple, Union

from dbterd.adapters.algos import base
from dbterd.adapters.meta import Ref, SemanticEntity, Table
from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def parse_metadata(data, **kwargs) -> Tuple[List[Table], List[Ref]]:
    """Get all information (tables, relationships) needed for building diagram
    (from Metadata, with Semantic Entities)

    Args:
        data (dict): metadata dict

    Returns:
        Tuple(List[Table], List[Ref]): Info of parsed tables and relationships
    """
    tables = []
    relationships = []

    # Parse Table
    tables = base.get_tables_from_metadata(data=data, **kwargs)
    tables = base.filter_tables_based_on_selection(tables=tables, **kwargs)

    # Parse Ref
    relationships = _get_relationships_from_metadata(data=data, **kwargs)
    relationships = base.make_up_relationships(
        relationships=relationships, tables=tables
    )

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (
        sorted(tables, key=lambda tbl: tbl.node_name),
        sorted(relationships, key=lambda rel: rel.name),
    )


def parse(
    manifest: Manifest, catalog: Union[str, Catalog], **kwargs
) -> Tuple[List[Table], List[Ref]]:
    # Parse metadata
    if catalog == "metadata":
        return parse_metadata(data=manifest, **kwargs)

    # Parse Table
    tables = base.get_tables(manifest=manifest, catalog=catalog, **kwargs)
    tables = base.filter_tables_based_on_selection(tables=tables, **kwargs)

    # Parse Ref
    relationships = _get_relationships(manifest=manifest, **kwargs)
    relationships = base.make_up_relationships(
        relationships=relationships, tables=tables
    )

    # Fulfill columns in Tables (due to `select *`)
    tables = base.enrich_tables_from_relationships(
        tables=tables, relationships=relationships
    )

    logger.info(
        f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
    )
    return (
        sorted(tables, key=lambda tbl: tbl.node_name),
        sorted(relationships, key=lambda rel: rel.name),
    )


def find_related_nodes_by_id(
    manifest: Union[Manifest, dict], node_unique_id: str, type: str = None, **kwargs
) -> List[str]:
    """Find FK/PK nodes which are linked to the given node

    Args:
        manifest (Union[Manifest, dict]): Manifest data
        node_unique_id (str): Manifest model node unique id
        type (str, optional): Manifest type (local file or metadata). Defaults to None.

    Returns:
        List[str]: Manifest nodes' unique ID
    """
    found_nodes = [node_unique_id]
    if type == "metadata":  # pragma: no cover
        return found_nodes  # not supported yet, returned input only

    entities = _get_linked_semantic_entities(manifest=manifest)
    for foreign, primary in entities:
        if primary.model == node_unique_id:
            found_nodes.append(foreign.model)
        if foreign.model == node_unique_id:
            found_nodes.append(primary.model)

    return list(set(found_nodes))


def _get_relationships_from_metadata(data=[], **kwargs) -> List[Ref]:
    """Extract relationships from Metadata result list on Semantic Entities

    Args:
        data (List): Metadata result list. Defaults to [].

    Returns:
        list[Ref]: List of parsed relationship
    """
    entities = _get_linked_semantic_entities_from_metadata(data=data)
    return base.get_unique_refs(
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


def _get_relationships(manifest: Manifest, **kwargs) -> List[Ref]:
    """_summary_

    Args:
        manifest (Manifest): Extract relationships from dbt artifacts based on Semantic Entities

    Returns:
        List[Ref]: List of parsed relationship
    """
    entities = _get_linked_semantic_entities(manifest=manifest)
    return base.get_unique_refs(
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
    data=[],
) -> List[Tuple[SemanticEntity, SemanticEntity]]:
    """Get filtered list of Semantic Entities which are linked
    (Metadata)

    Args:
        data (List): Metadata result list. Defaults to [].

    Returns:
        List[Tuple[SemanticEntity, SemanticEntity]]: List of (FK, PK) objects
    """
    foreigns, primaries = _get_semantic_entities_from_metadata(data=data)
    linked_entities = []
    for foreign_entity in foreigns:
        for primary_entity in primaries:
            if foreign_entity.entity_name == primary_entity.entity_name:
                linked_entities.append((foreign_entity, primary_entity))
    return linked_entities


def _get_linked_semantic_entities(
    manifest: Manifest,
) -> List[Tuple[SemanticEntity, SemanticEntity]]:
    """Get filtered list of Semantic Entities which are linked

    Args:
        manifest (Manifest): Manifest data

    Returns:
        List[Tuple[SemanticEntity, SemanticEntity]]: List of (FK, PK) objects
    """
    foreigns, primaries = _get_semantic_entities(manifest=manifest)
    linked_entities = []
    for foreign_entity in foreigns:
        for primary_entity in primaries:
            if foreign_entity.entity_name == primary_entity.entity_name:
                linked_entities.append((foreign_entity, primary_entity))
    return linked_entities


def _get_semantic_entities_from_metadata(
    data=[],
) -> Tuple[List[SemanticEntity], List[SemanticEntity]]:
    """Get all Semantic Entities
    (Metadata)

    Args:
        data (List): Metadata result list. Defaults to [].

    Returns:
        Tuple[List[SemanticEntity], List[SemanticEntity]]: FK list and PK list
    """
    FK = "foreign"
    PK = "primary"

    semantic_entities = []
    for data_item in data:
        for semantic_model in data_item.get("semanticModels", {}).get("edges", []):
            id = semantic_model.get("node", {}).get("uniqueId", "")
            meta = semantic_model.get("node", {}).get("meta", {}) or {}
            # currently only 1 parent with rs type of "model"
            model_id = (
                semantic_model.get("node", {}).get("parents", {})[0].get("uniqueId", "")
            )

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
                        relationship_type=(
                            meta.get(TEST_META_RELATIONSHIP_TYPE, "") if meta else ""
                        ),
                    )
                )

    return (
        [x for x in semantic_entities if x.entity_type == FK],
        [x for x in semantic_entities if x.entity_type == PK],
    )


def _get_semantic_entities(
    manifest: Manifest,
) -> Tuple[List[SemanticEntity], List[SemanticEntity]]:
    """Get all Semantic Entities

    Args:
        manifest (Manifest): Manifest data

    Returns:
        Tuple[List[SemanticEntity], List[SemanticEntity]]: FK list and PK list
    """
    FK = "foreign"
    PK = "primary"

    semantic_entities = []
    for x in _get_semantic_nodes(manifest=manifest):
        semantic_node = manifest.semantic_models[x]
        for e in semantic_node.entities:
            if e.type.value in [PK, FK]:
                semantic_entities.append(
                    SemanticEntity(
                        semantic_model=x,
                        model=semantic_node.depends_on.nodes[0],
                        entity_name=e.name,
                        entity_type=e.type.value,
                        column_name=e.expr or e.name,
                        relationship_type=semantic_node.config.meta.get(
                            TEST_META_RELATIONSHIP_TYPE, ""
                        ),
                    )
                )
        if semantic_node.primary_entity:
            semantic_entities.append(
                SemanticEntity(
                    semantic_model=x,
                    model=semantic_node.depends_on.nodes[0],
                    entity_name=semantic_node.primary_entity,
                    entity_type=PK,
                    column_name=semantic_node.primary_entity,
                    relationship_type=semantic_node.config.meta.get(
                        TEST_META_RELATIONSHIP_TYPE, ""
                    ),
                )
            )

    return (
        [x for x in semantic_entities if x.entity_type == FK],
        [x for x in semantic_entities if x.entity_type == PK],
    )


def _get_semantic_nodes(manifest: Manifest) -> List:
    """Extract the Semantic Models

    Args:
        manifest (Manifest): Manifest data

    Returns:
        List: List of Semantic Models
    """
    if not hasattr(manifest, "semantic_models"):
        logger.warning(
            "No relationships will be captured"
            "since dbt version is NOT supported for the Semantic Models"
        )
        return []

    return [
        x
        for x in manifest.semantic_models
        if len(manifest.semantic_models[x].depends_on.nodes)
    ]
