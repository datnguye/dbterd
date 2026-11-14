from pathlib import Path
from unittest import mock

from artifact_parser.core import OptionalDependencyError
from artifact_parser.dbt_info_schema import InfoSchemaV1, parse_info_schema
import click
import pytest

from dbterd.adapters.algos.model_contract import ModelContractAlgo
from dbterd.adapters.algos.semantic import SemanticAlgo
from dbterd.adapters.algos.test_relationship import TestRelationshipAlgo
from dbterd.api import DbtErd
from dbterd.cli.main import DbterdRunner
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Column
from dbterd.helpers import file


SAMPLES = Path(__file__).parents[4] / "samples"
JAFFLE_V2 = SAMPLES / "jaffle-shop-v2"
JAFFLE_V2_OSS_INFO = SAMPLES / "jaffle-shop-v2-oss" / "info_schema" / "v1"
OPTIONS = {
    "select": [],
    "exclude": [],
    "resource_type": ["model", "source", "seed", "snapshot"],
    "entity_name_format": "resource.package.model",
}
ALGOS = [
    (TestRelationshipAlgo, "test_relationship", 3),
    (SemanticAlgo, "semantic", 4),
    (ModelContractAlgo, "model_contract", 0),
]


def _refs(relationships):
    return sorted((r.name, tuple(r.table_map), tuple(map(tuple, r.column_map)), r.type) for r in relationships)


def _parse_json(algo_class, algo):
    manifest = file.read_manifest(path=str(JAFFLE_V2), version=12)
    catalog = file.read_catalog(path=str(JAFFLE_V2), version=1)
    return algo_class().parse(manifest=manifest, catalog=catalog, algo=algo, **OPTIONS)


def _parse_info(algo_class, algo, path=JAFFLE_V2 / "info_schema" / "v1"):
    return algo_class().parse(manifest=parse_info_schema(path), catalog="info_schema", algo=algo, **OPTIONS)


def _info(**tables):
    return InfoSchemaV1(dbt_project=[{"schema_version": 1}], **tables)


def _model(name, **fields):
    return {"unique_id": f"model.pkg.{name}", "name": name, "database_name": "DB", "schema_name": "S", **fields}


def _column(node, name, **fields):
    return {"node_unique_id": node, "column_name": name, **fields}


class NoInfoAlgo(BaseAlgoAdapter):
    def parse_artifacts(self, manifest, catalog, **kwargs):
        return [], []

    def parse_metadata(self, data, **kwargs):
        return [], []


class TestEquivalence:
    @pytest.mark.parametrize("algo_class, algo, expected_refs", ALGOS)
    def test_same_relationships_and_tables_as_json(self, algo_class, algo, expected_refs):
        json_tables, json_refs = _parse_json(algo_class, algo)
        info_tables, info_refs = _parse_info(algo_class, algo)

        assert len(info_refs) == expected_refs
        assert _refs(info_refs) == _refs(json_refs)
        assert [t.name for t in info_tables] == [t.name for t in json_tables]

    @pytest.mark.parametrize("algo_class, algo, expected_refs", ALGOS)
    def test_oss_engine_output(self, algo_class, algo, expected_refs):
        _, refs = _parse_info(algo_class, algo, path=JAFFLE_V2_OSS_INFO)
        assert len(refs) == expected_refs

    @pytest.mark.parametrize("algo_class, algo, expected_refs", ALGOS)
    def test_find_related_nodes(self, algo_class, algo, expected_refs):
        info = parse_info_schema(JAFFLE_V2 / "info_schema" / "v1")
        related = algo_class().find_related_nodes_by_id(
            manifest=info, node_unique_id="model.jaffle_shop.orders", type="info_schema", algo=algo
        )
        assert "model.jaffle_shop.orders" in related
        assert (len(related) > 1) == (expected_refs > 0)


class TestTables:
    def test_get_tables_from_info_schema(self):
        info = _info(
            dbt_models=[
                _model("orders", identifier="ORDERS_TBL", meta={"label": "Orders"}, compiled_code="select 1"),
                _model("off", enabled=False),
            ],
            dbt_sources=[{"unique_id": "source.pkg.raw.items", "name": "items", "alias": "items"}],
            dbt_node_columns=[
                _column("model.pkg.orders", "b", column_index=1, data_type_inferred="Utf8", data_type_declared="text"),
                _column("model.pkg.orders", '"A"', column_index=0, data_type_actual="INT", description="a"),
            ],
            dbt_edges=[
                {"parent_unique_id": "source.pkg.raw.items", "child_unique_id": "model.pkg.orders"},
                {"parent_unique_id": "model.pkg.orders", "child_unique_id": "exposure.pkg.dash"},
            ],
        )
        tables = BaseAlgoAdapter.get_tables_from_info_schema(
            TestRelationshipAlgo(), info=info, entity_name_format="database.schema.table"
        )

        orders, items = tables
        assert orders.name == "db.s.orders_tbl"
        assert [(c.name, c.data_type, c.description) for c in orders.columns] == [("a", "int", "a"), ("b", "text", "")]
        assert orders.exposures == ["dash"]
        assert orders.raw_depends_on == ["source.pkg.raw.items"]
        assert orders.label == "Orders"
        assert orders.raw_sql == "select 1"
        assert items.name == "KEYNOTFOUND.KEYNOTFOUND.items"
        assert items.columns == [Column()]

    def test_algo_without_info_schema_support(self):
        with pytest.raises(click.UsageError, match="`custom` does not support the dbt info schema"):
            NoInfoAlgo().parse(manifest=_info(), catalog="info_schema", algo="custom")


class TestTestRelationship:
    def test_skipped_tests(self):
        test = {"node_unique_id": "model.pkg.a", "arguments": {"column_name": "x", "field": "y"}}
        info = _info(
            dbt_data_tests=[
                {**test, "unique_id": "test.pkg.relationships_self"},
                {**test, "unique_id": "test.pkg.relationships_orphan"},
                {**test, "unique_id": "test.pkg.relationships_ignored", "meta": {"ignore_in_erd": 1}},
                {**test, "unique_id": "test.pkg.relationships_disabled", "enabled": False},
                {**test, "unique_id": "test.pkg.not_null_a_x"},
            ],
            dbt_edges=[
                {"parent_unique_id": "model.pkg.a", "child_unique_id": f"test.pkg.relationships_{x}"}
                for x in ["self", "ignored", "disabled"]
            ],
        )
        refs = TestRelationshipAlgo().get_relationships_from_info_schema(info=info, algo="test_relationship")
        assert _refs(refs) == [("test.pkg.relationships_self", ("model.pkg.a", "model.pkg.a"), (("y",), ("x",)), "n1")]


class TestModelContract:
    def test_constraints(self):
        fk = {"type": "foreign_key", "to": "ref('customers')"}
        info = _info(
            dbt_models=[
                _model("customers", constraints=[{"type": "primary_key", "columns": ["ID"]}]),
                _model(
                    "orders",
                    meta={"relationship_types": {"fk_m": "one-to-one"}, "relationship_label": "places"},
                    constraints=[
                        {**fk, "name": "fk_m", "columns": ["c1"], "to_columns": ["id"]},
                        {**fk, "columns": ["c2"]},
                        {**fk},
                        {**fk, "to": "nowhere", "columns": ["c3"]},
                    ],
                ),
            ],
            dbt_node_columns=[
                _column("model.pkg.customers", "id"),
                _column("model.pkg.customers", "code", constraints=[{"type": "primary_key"}]),
                _column(
                    "model.pkg.orders",
                    "customer_id",
                    meta={"relationship_type": "zero-to-many"},
                    constraints=[{**fk, "to_columns": ["id", "code"]}, {**fk, "to": "nowhere"}],
                ),
                _column("model.pkg.orders", "cust", constraints=[{**fk, "name": "fk_c"}]),
                _column("model.pkg.gone", "x", constraints=[fk]),
                _column("seed.pkg.s", "x", constraints=[fk]),
            ],
        )
        tables, refs = ModelContractAlgo().parse(manifest=info, catalog="info_schema", **OPTIONS)

        customers = next(t for t in tables if t.node_name == "model.pkg.customers")
        assert [c.name for c in customers.columns if c.is_primary_key] == ["id", "code"]
        customers_name, orders_name = "model.pkg.customers", "model.pkg.orders"
        assert _refs(refs) == [
            ("fk_c", (customers_name, orders_name), (("cust",), ("cust",)), "n1"),
            ("fk_m", (customers_name, orders_name), (("id",), ("c1",)), "11"),
            ("model.pkg.orders", (customers_name, orders_name), (("c2",), ("c2",)), "n1"),
            ("model.pkg.orders", (customers_name, orders_name), (("code",), ("customer_id",)), "0n"),
            ("model.pkg.orders", (customers_name, orders_name), (("id",), ("customer_id",)), "0n"),
        ]


class TestSemantic:
    def test_primary_entity_and_unmapped_models(self):
        info = _info(
            dbt_semantic_models=[
                {"unique_id": "semantic_model.pkg.customers", "primary_entity": "customer"},
                {"unique_id": "semantic_model.pkg.orders", "config": {"meta": {"relationship_type": "one-to-one"}}},
                {"unique_id": "semantic_model.pkg.unmapped", "primary_entity": "customer"},
            ],
            dbt_semantic_entities=[
                {"unique_id": "semantic_model.pkg.orders", "name": "customer", "entity_type": "foreign"},
                {"unique_id": "semantic_model.pkg.orders", "name": "order", "entity_type": "primary", "expr": "id"},
                {"unique_id": "semantic_model.pkg.orders", "name": "ts", "entity_type": "natural"},
                {"unique_id": "semantic_model.pkg.unmapped", "name": "customer", "entity_type": "foreign"},
            ],
            dbt_edges=[
                {"parent_unique_id": "model.pkg.customers", "child_unique_id": "semantic_model.pkg.customers"},
                {"parent_unique_id": "model.pkg.orders", "child_unique_id": "semantic_model.pkg.orders"},
            ],
        )
        refs = SemanticAlgo().get_relationships_from_info_schema(info=info)
        assert _refs(refs) == [
            (
                "semantic_model.pkg.customers",
                ("model.pkg.customers", "model.pkg.orders"),
                (("customer",), ("customer",)),
                "n1",
            )
        ]


class TestExecutor:
    @pytest.mark.parametrize(
        "info_schema, expected",
        [
            (True, str(JAFFLE_V2 / "info_schema" / "v1")),
            ("some/dir", str(Path("some/dir").absolute())),
            (None, None),
        ],
    )
    def test_evaluate_kwargs(self, dummy_executor, info_schema, expected):
        kwargs = dummy_executor.evaluate_kwargs(
            artifacts_dir=str(JAFFLE_V2), select=[], exclude=[], info_schema=info_schema
        )
        assert kwargs["artifacts_dir"] == str(JAFFLE_V2)
        assert kwargs["info_schema"] == expected

    def test_get_dir_falls_back_to_target(self, dummy_executor):
        artifacts_dir, _ = dummy_executor._get_dir(artifacts_dir=str(SAMPLES), info_schema=True)
        assert artifacts_dir == str(SAMPLES / "target")

    def test_missing_info_schema_dir(self, dummy_executor, tmp_path):
        with pytest.raises(click.FileError, match="Info schema directory does not exist"):
            dummy_executor._read_info_schema(str(tmp_path / "info_schema" / "v1"))

    def test_missing_pyarrow(self, dummy_executor):
        with (
            mock.patch("dbterd.core.executor.parse_info_schema", side_effect=OptionalDependencyError("no pyarrow")),
            pytest.raises(click.UsageError, match=r"dbterd\[info-schema\]"),
        ):
            dummy_executor._read_info_schema(str(JAFFLE_V2))

    def test_api_model_erd(self):
        erd = DbtErd(artifacts_dir=str(JAFFLE_V2), info_schema=True, target="mermaid").get_model_erd(
            node_unique_id="model.jaffle_shop.orders"
        )
        assert '"MODEL.JAFFLE_SHOP.ORDER_ITEMS" }|--|| "MODEL.JAFFLE_SHOP.ORDERS"' in erd
        assert "MODEL.JAFFLE_SHOP.STG_ORDERS" not in erd

    def test_cli_flag(self, tmp_path):
        DbterdRunner().invoke(["run", "--info-schema", str(JAFFLE_V2_OSS_INFO), "-o", str(tmp_path)])
        assert "Ref: " in (tmp_path / "output.dbml").read_text()
