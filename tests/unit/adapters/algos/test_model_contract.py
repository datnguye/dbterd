from typing import ClassVar
from unittest import mock

import pytest

from dbterd.adapters.algos.model_contract import (
    ModelContractAlgo,
    _get_relationship_type,
    _resolve_ref_to_node_id,
)
from dbterd.core.models import Ref
from tests.unit.adapters.algos import (
    ConstraintType,
    DummyManifestNoConstraintsAttr,
    DummyManifestWithColumnLevelConstraints,
    DummyManifestWithModelLevelConstraints,
    ManifestNodeColumnWithConstraints,
    ManifestNodeConstraint,
    ManifestNodeWithConstraints,
)


class TestResolveRefToNodeId:
    NODES: ClassVar[dict] = {
        "model.pkg.customers": None,
        "model.pkg.orders": None,
        "model.other_pkg.customers": None,
        "seed.pkg.raw_data": None,
    }

    @pytest.mark.parametrize(
        "ref_str, expected",
        [
            ("ref('customers')", "model.pkg.customers"),
            ('ref("customers")', "model.pkg.customers"),
            ("ref('pkg', 'customers')", "model.pkg.customers"),
            ('ref("pkg", "customers")', "model.pkg.customers"),
            ("ref('orders')", "model.pkg.orders"),
            ("ref('nonexistent')", None),
            ("", None),
            ("not_a_ref", None),
            ("ref()", None),
        ],
    )
    def test_resolve_ref(self, ref_str, expected):
        result = _resolve_ref_to_node_id(ref_str, self.NODES)
        assert result == expected


class TestGetRelationshipType:
    @pytest.mark.parametrize(
        "meta_value, expected",
        [
            ("zero-to-many", "0n"),
            ("zero-to-one", "01"),
            ("one-to-one", "11"),
            ("many-to-many", "nn"),
            ("one-to-many", "1n"),
            ("many-to-one", "n1"),
            ("--irrelevant--", "n1"),
            ("", "n1"),
        ],
    )
    def test_get_relationship_type(self, meta_value, expected):
        assert _get_relationship_type(meta_value) == expected


class TestAlgoModelContract:
    def test_get_relationships_column_level_fk(self):
        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=DummyManifestWithColumnLevelConstraints())
        assert len(refs) == 2
        assert (
            Ref(
                name="model.pkg.orders",
                table_map=["model.pkg.customers", "model.pkg.orders"],
                column_map=["id", "customer_id"],
                type="n1",
            )
            in refs
        )
        assert (
            Ref(
                name="model.pkg.orders",
                table_map=["model.pkg.products", "model.pkg.orders"],
                column_map=["id", "product_id"],
                type="n1",
            )
            in refs
        )

    def test_get_relationships_model_level_fk(self):
        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=DummyManifestWithModelLevelConstraints())
        assert (
            Ref(
                name="model.pkg.orders",
                table_map=["model.pkg.customers", "model.pkg.orders"],
                column_map=["id", "customer_id"],
                type="n1",
            )
            in refs
        )

    def test_get_relationships_model_level_composite_fk(self):
        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=DummyManifestWithModelLevelConstraints())
        assert (
            Ref(
                name="model.pkg.orders",
                table_map=["model.pkg.departments", "model.pkg.orders"],
                column_map=["org_id", "org_id"],
                type="n1",
            )
            in refs
        )
        assert (
            Ref(
                name="model.pkg.orders",
                table_map=["model.pkg.departments", "model.pkg.orders"],
                column_map=["dept_id", "dept_id"],
                type="n1",
            )
            in refs
        )

    def test_get_relationships_non_fk_ignored(self):
        """Nodes with only primary_key/not_null/unique constraints produce no refs."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={
                        "id": ManifestNodeColumnWithConstraints(
                            name="id",
                            constraints=[
                                ManifestNodeConstraint(type=ConstraintType("primary_key")),
                                ManifestNodeConstraint(type=ConstraintType("not_null")),
                                ManifestNodeConstraint(type=ConstraintType("unique")),
                            ],
                        ),
                    },
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_fk_without_to(self):
        """FK constraint without `to` field (pre-v12) is skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={
                        "fk_col": ManifestNodeColumnWithConstraints(
                            name="fk_col",
                            constraints=[
                                ManifestNodeConstraint(type=ConstraintType("foreign_key"), to=None),
                            ],
                        ),
                    },
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_no_constraints_attr(self):
        """Nodes from older manifests without constraints attr produce no refs."""
        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=DummyManifestNoConstraintsAttr()) == []

    def test_get_relationships_empty_manifest(self):
        class _Manifest:
            nodes: ClassVar[dict] = {}

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_no_nodes_attr(self):
        class _Manifest:
            pass

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_skips_non_model_nodes(self):
        class _Manifest:
            nodes: ClassVar[dict] = {
                "seed.pkg.raw_data": ManifestNodeWithConstraints(columns={}),
                "test.pkg.some_test": ManifestNodeWithConstraints(columns={}),
                "snapshot.pkg.snap1": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_unresolvable_ref(self):
        """FK with ref to a deleted/nonexistent model is skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={
                        "fk_col": ManifestNodeColumnWithConstraints(
                            name="fk_col",
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('deleted_model')",
                                    to_columns=["id"],
                                ),
                            ],
                        ),
                    },
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_fk_without_to_columns(self):
        """FK with to but no to_columns falls back to from column name."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={
                        "customer_id": ManifestNodeColumnWithConstraints(
                            name="customer_id",
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('customers')",
                                    to_columns=None,
                                ),
                            ],
                        ),
                    },
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1
        assert refs[0].column_map == ["customer_id", "customer_id"]

    def test_get_relationships_self_referential(self):
        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.employee": ManifestNodeWithConstraints(
                    columns={
                        "manager_id": ManifestNodeColumnWithConstraints(
                            name="manager_id",
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('employee')",
                                    to_columns=["id"],
                                ),
                            ],
                        ),
                    },
                ),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1
        assert refs[0].table_map == ["model.pkg.employee", "model.pkg.employee"]

    def test_get_relationships_with_relationship_type(self):
        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={
                        "customer_id": ManifestNodeColumnWithConstraints(
                            name="customer_id",
                            meta={"relationship_type": "one-to-one"},
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('customers')",
                                    to_columns=["id"],
                                ),
                            ],
                        ),
                    },
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1
        assert refs[0].type == "11"

    def test_get_relationships_model_level_fk_no_columns(self):
        """Model-level FK without columns field is skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to="ref('customers')",
                            to_columns=["id"],
                            columns=None,
                        ),
                    ],
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_model_level_fk_no_to_columns(self):
        """Model-level FK without to_columns falls back to columns."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to="ref('customers')",
                            to_columns=None,
                            columns=["customer_id"],
                        ),
                    ],
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1
        assert refs[0].column_map == ["customer_id", "customer_id"]

    def test_get_relationships_model_level_with_relationship_type(self):
        """Model-level meta.relationship_type is respected."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={},
                    meta={"relationship_type": "one-to-many"},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to="ref('customers')",
                            to_columns=["id"],
                            columns=["customer_id"],
                        ),
                    ],
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1
        assert refs[0].type == "1n"

    def test_get_relationships_deduplication(self):
        """Duplicate FK constraints (same table_map + column_map) are deduplicated."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={
                        "customer_id": ManifestNodeColumnWithConstraints(
                            name="customer_id",
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('customers')",
                                    to_columns=["id"],
                                ),
                            ],
                        ),
                    },
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to="ref('customers')",
                            to_columns=["id"],
                            columns=["customer_id"],
                        ),
                    ],
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        refs = algo.get_relationships(manifest=_Manifest())
        assert len(refs) == 1

    def test_get_relationships_column_with_empty_constraints(self):
        """Column with empty constraints list produces no refs."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={
                        "col1": ManifestNodeColumnWithConstraints(name="col1", constraints=[]),
                    },
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_parse_artifacts(self):
        with (
            mock.patch.object(ModelContractAlgo, "get_tables") as mock_get_tables,
            mock.patch.object(ModelContractAlgo, "get_relationships") as mock_get_relationships,
        ):
            mock_get_tables.return_value = []
            mock_get_relationships.return_value = []

            algo = ModelContractAlgo()
            algo.parse_artifacts(
                manifest="--manifest--",
                catalog="--catalog--",
                select=[],
                exclude=[],
                resource_type=["model"],
            )
            mock_get_tables.assert_called_once()
            mock_get_relationships.assert_called_once()

    def test_parse_metadata_not_supported(self):
        algo = ModelContractAlgo()
        result = algo.parse_metadata(data=[], select=[], exclude=[], resource_type=["model"])
        assert result == ([], [])

    def test_find_related_nodes_by_id_fk_source(self):
        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(
            manifest=DummyManifestWithColumnLevelConstraints(),
            node_unique_id="model.pkg.orders",
        )
        assert sorted(result) == sorted(["model.pkg.orders", "model.pkg.customers", "model.pkg.products"])

    def test_find_related_nodes_by_id_fk_target(self):
        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(
            manifest=DummyManifestWithColumnLevelConstraints(),
            node_unique_id="model.pkg.customers",
        )
        assert sorted(result) == sorted(["model.pkg.customers", "model.pkg.orders"])

    def test_find_related_nodes_by_id_no_match(self):
        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(
            manifest=DummyManifestWithColumnLevelConstraints(),
            node_unique_id="model.pkg.nonexistent",
        )
        assert result == ["model.pkg.nonexistent"]

    def test_find_related_nodes_by_id_metadata_type(self):
        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(
            manifest=DummyManifestWithColumnLevelConstraints(),
            node_unique_id="model.pkg.orders",
            type="metadata",
        )
        assert result == ["model.pkg.orders"]

    def test_find_related_nodes_by_id_no_nodes_attr(self):
        class _Manifest:
            pass

        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(manifest=_Manifest(), node_unique_id="model.pkg.orders")
        assert result == ["model.pkg.orders"]

    def test_find_related_nodes_by_id_model_level_constraints(self):
        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(
            manifest=DummyManifestWithModelLevelConstraints(),
            node_unique_id="model.pkg.orders",
        )
        assert "model.pkg.customers" in result
        assert "model.pkg.departments" in result

    def test_find_related_nodes_by_id_skips_non_model_nodes(self):
        class _Manifest:
            nodes: ClassVar[dict] = {
                "seed.pkg.raw": ManifestNodeWithConstraints(columns={}),
                "model.pkg.orders": ManifestNodeWithConstraints(
                    columns={
                        "customer_id": ManifestNodeColumnWithConstraints(
                            name="customer_id",
                            constraints=[
                                ManifestNodeConstraint(
                                    type=ConstraintType("foreign_key"),
                                    to="ref('customers')",
                                    to_columns=["id"],
                                ),
                            ],
                        ),
                    },
                ),
                "model.pkg.customers": ManifestNodeWithConstraints(columns={}),
            }

        algo = ModelContractAlgo()
        result = algo.find_related_nodes_by_id(manifest=_Manifest(), node_unique_id="model.pkg.orders")
        assert sorted(result) == sorted(["model.pkg.orders", "model.pkg.customers"])

    def test_get_relationships_model_level_non_fk_ignored(self):
        """Model-level non-FK constraints are skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("primary_key"),
                            columns=["id"],
                        ),
                        ManifestNodeConstraint(
                            type=ConstraintType("unique"),
                            columns=["email"],
                        ),
                    ],
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_model_level_fk_without_to(self):
        """Model-level FK without `to` field is skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to=None,
                            columns=["fk_col"],
                        ),
                    ],
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []

    def test_get_relationships_model_level_unresolvable_ref(self):
        """Model-level FK with unresolvable ref is skipped."""

        class _Manifest:
            nodes: ClassVar[dict] = {
                "model.pkg.t1": ManifestNodeWithConstraints(
                    columns={},
                    constraints=[
                        ManifestNodeConstraint(
                            type=ConstraintType("foreign_key"),
                            to="ref('nonexistent')",
                            to_columns=["id"],
                            columns=["fk_col"],
                        ),
                    ],
                ),
            }

        algo = ModelContractAlgo()
        assert algo.get_relationships(manifest=_Manifest()) == []
