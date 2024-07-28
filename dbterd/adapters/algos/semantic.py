from typing import List, Tuple, Union

from dbterd.adapters.algos import base
from dbterd.adapters.meta import Ref, SemanticEntity, Table
from dbterd.constants import TEST_META_RELATIONSHIP_TYPE
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


def parse_metadata(data, **kwargs) -> Tuple[List[Table], List[Ref]]:
    raise NotImplementedError()


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
    raise NotImplementedError()


def _get_relationships(manifest: Manifest, **kwargs) -> List[Ref]:
    """_summary_

    Args:
        manifest (Manifest): _description_

    Returns:
        List[Ref]: _description_
    """
    if not hasattr(manifest, "semantic_models"):
        logger.warning(
            "No relationships will be captured"
            "since dbt version is NOT supported for the Semantic Models"
        )
        return []

    FK = "foreign"
    PK = "primary"

    semantic_entities = []
    for x in manifest.semantic_models:
        if not len(manifest.semantic_models[x].depends_on.nodes):
            continue

        for e in manifest.semantic_models[x].entities:
            if e.type.value in [PK, FK]:
                semantic_entities.append(
                    SemanticEntity(
                        semantic_model=x,
                        model=manifest.semantic_models[x].depends_on.nodes[0],
                        entity_name=e.name,
                        entity_type=e.type.value,
                        column_name=e.expr or e.name,
                    )
                )

    refs = []
    foreigns = [x for x in semantic_entities if x.entity_type == FK]
    primaries = [x for x in semantic_entities if x.entity_type == PK]
    for foreign_entity in foreigns:
        for primary_entity in primaries:
            if foreign_entity.entity_name == primary_entity.entity_name:
                refs.append(
                    Ref(
                        name=primary_entity.semantic_model,
                        table_map=(primary_entity.model, foreign_entity.model),
                        column_map=(
                            foreign_entity.column_name,
                            primary_entity.column_name,
                        ),
                        type=manifest.semantic_models[x].config.meta.get(
                            TEST_META_RELATIONSHIP_TYPE, ""
                        ),
                    )
                )

    return refs
