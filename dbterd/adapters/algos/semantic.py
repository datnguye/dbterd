from typing import List, Tuple, Union

from dbterd.adapters.algos import base
from dbterd.adapters.meta import Ref, Table
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
    if not hasattr(manifest, "semantic_models"):
        logger.warning("dbt version is NOT supported for the Semantic Models")
        return []

    semantic_entities = []
    for x in manifest.semantic_models:
        if not len(manifest.semantic_models[x].depends_on.nodes):
            continue

        for e in manifest.semantic_models[x].entities:
            if e.type.value not in ["primary", "foreign"]:
                continue

            entity_info = dict(
                e=x, m=manifest.semantic_models[x].depends_on.nodes[0], pk=None, fk=None
            )
            if e.type.value == "primary":
                entity_info["pk"] = dict(
                    name=e.name, type=e.type.value, column_name=e.expr or e.name
                )
            if e.type.value == "foreign":
                entity_info["fk"] = dict(
                    name=e.name, type=e.type.value, column_name=e.expr or e.name
                )
            semantic_entities.append(entity_info)

    refs = []
    for from_e in [x for x in semantic_entities if x.get("fk")]:
        fk_entity_name = from_e.get("fk", {}).get("name")
        fk_column_name = from_e.get("fk", {}).get("column_name")

        for to_e in [x for x in semantic_entities if x.get("pk")]:
            pk_entity_name = to_e.get("pk", {}).get("name")
            pk_column_name = to_e.get("pk", {}).get("column_name")

            if fk_entity_name == pk_entity_name:
                refs.append(
                    Ref(
                        name=from_e.get("e"),
                        table_map=(to_e.get("m"), from_e.get("m")),
                        column_map=(fk_column_name, pk_column_name),
                        type=manifest.semantic_models[x].config.meta.get(
                            TEST_META_RELATIONSHIP_TYPE, ""
                        ),
                    )
                )

    return refs
