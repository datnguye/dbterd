# Implementation Plan: Model Contract Constraints Algorithm

> GitHub Issue: [#95 - Use DBT model contracts](https://github.com/datnguye/dbterd/issues/95)
> dbt Docs: [Constraints Reference (v1.12)](https://docs.getdbt.com/reference/resource-properties/constraints?version=1.12)

## Context

dbt introduced [model contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts) in v1.5, allowing users to define column-level and model-level constraints (primary_key, foreign_key, unique, not_null, check, custom) directly in YAML. Since **dbt v1.9**, foreign key constraints support `ref()`, which populates the `to` and `to_columns` fields in `manifest.json`. This makes it possible to extract FK relationships from constraints without parsing raw SQL expressions.

dbterd currently has two relationship-detection algorithms:
- `test_relationship` (default) - extracts from dbt relationship tests
- `semantic` - extracts from Semantic Layer entity definitions

This plan adds a third: **`model_contract`** - extracts from dbt model contract constraints.

**Scope**: dbt Core (file-based artifacts) only. dbt Cloud metadata API support is out of scope for this iteration.

## Prerequisites / Parser Support

**Installed**: `dbt-artifacts-parser==0.11.0` (pinned `>=0.10.0`). Latest available: `0.12.0`.

### Verified constraint field availability (from installed package inspection)

| Manifest Version | Column `constraints` | Node `constraints` | `to` / `to_columns` |
|---|---|---|---|
| v1-v8 | No | No | No |
| v9-v11 | Yes (`ColumnLevelConstraint`: 5 fields) | No | **No** |
| **v12** (dbt 1.9+) | **Yes** (`Constraint`/`Constraint4`: 7 fields) | **Yes** (`Constraint5`: 8 fields) | **Yes** |

### v12 class details (verified via `inspect`)

**Column-level constraint** (`Constraint4` on `Columns4`, used by `Nodes4`/model):
```python
type: Type           # Enum: check, not_null, unique, primary_key, foreign_key, custom
name: Optional[str]
expression: Optional[str]
warn_unenforced: Optional[bool]
warn_unsupported: Optional[bool]
to: Optional[str]              # FK target model ref
to_columns: Optional[List[str]]  # FK target columns
```

**Model-level constraint** (`Constraint5` on `Nodes4`/model) -- same as above plus:
```python
columns: Optional[List[str]]  # Which columns this constraint applies to
```

### v12 node type mapping (verified)

| Class | resource_type | has `constraints` | has `columns` |
|---|---|---|---|
| `Nodes` | `seed` | No | Yes (but columns lack constraints) |
| `Nodes4` | `model` | **Yes** | **Yes** (columns have constraints) |
| `Nodes7` | `snapshot` | No | Yes (columns lack constraints) |
| `Nodes1` | `analysis` | No | Yes |
| `Nodes2`/`Nodes6` | `test` | No | Yes |
| `Nodes3` | `operation` | No | Yes |

**Key finding**: Only `model` nodes (`Nodes4`) have both node-level and column-level constraints. Seeds and snapshots do not have constraint fields at all.

### v9-v11 `ColumnLevelConstraint` (verified -- lacks `to`/`to_columns`)
```python
type, name, expression, warn_unenforced, warn_unsupported  # NO to, NO to_columns
```

**Decision**: Target manifest v12+ only. Older manifests will produce zero relationships with a warning log. Only `model.*` nodes will be scanned for constraints (seeds/snapshots don't support them).

---

## Step-by-Step Implementation

### Step 1: Create `dbterd/adapters/algos/model_contract.py`

New algorithm adapter module, following the same pattern as `test_relationship.py` and `semantic.py`.

**Key design decisions:**
- Register as `model_contract` via `@register_algo("model_contract", ...)`
- Subclass `BaseAlgoAdapter`
- Extract FK relationships from both **column-level** and **model-level** constraints
- Only process `foreign_key` constraint type (other types don't define inter-table relationships)
- Require `constraint.to` to be populated (v12+); skip constraints without it

**File structure:**

```python
@register_algo("model_contract", description="Detect relationships via dbt model contract constraints")
class ModelContractAlgo(BaseAlgoAdapter):

    def parse_artifacts(self, manifest, catalog, **kwargs):
        # 1. get_tables() from base class (same as other algos)
        # 2. get_relationships() - new method
        # 3. make_up_relationships() from base class
        # 4. enrich_tables_from_relationships() from base class

    def parse_metadata(self, data, **kwargs):
        # Not supported -- log warning and return ([], [])
        # parse_metadata is abstract in BaseAlgoAdapter so must be implemented
        # dbt Cloud metadata API constraint support is out of scope

    def find_related_nodes_by_id(self, manifest, node_unique_id, type=None, **kwargs):
        # Iterate model nodes, check constraints for FK refs to/from node_unique_id
        # Only supports file-based manifest (type != "metadata")

    def get_relationships(self, manifest, **kwargs):
        # Core logic: iterate model.* nodes only,
        # check column-level and model-level constraints,
        # build Ref objects from foreign_key constraints
```

**Core extraction logic in `get_relationships()`:**

```
For each node_name, node in manifest.nodes (model.* only -- seeds/snapshots lack constraints):
    # Check hasattr(node, 'constraints') and hasattr on columns for safety across manifest versions

    # Column-level constraints (Columns4 -> Constraint4)
    For each col_name, col in node.columns.items():
        If not hasattr(col, 'constraints') or not col.constraints: continue
        For each constraint in col.constraints:
            If constraint.type.value == "foreign_key" and constraint.to:
                - to_node_id = _resolve_ref_to_node_id(constraint.to, manifest.nodes)
                - from_column = col_name
                - to_column = constraint.to_columns[0] if constraint.to_columns else col_name
                - relationship_type = (col.meta or {}).get("relationship_type", "")
                - Build Ref(name=node_name, table_map=[to_node_id, node_name],
                            column_map=[to_column, from_column])

    # Model-level constraints (Nodes4 -> Constraint5, has `columns` field)
    If not hasattr(node, 'constraints') or not node.constraints: continue
    For each constraint in node.constraints:
        If constraint.type.value == "foreign_key" and constraint.to and constraint.columns:
            - to_node_id = _resolve_ref_to_node_id(constraint.to, manifest.nodes)
            - For each pair in zip(constraint.columns, constraint.to_columns or constraint.columns):
                - Build Ref per column pair
```

**Resolving `constraint.to` to a node ID:**

The `to` field contains a ref string like `ref('model_name')` or `ref('package', 'model_name')`. We need a helper to resolve this to a manifest node unique ID (e.g., `model.package.model_name`).

Approach: Search `manifest.nodes` keys for a match on the model name suffix. This mirrors how `test_relationship.py` resolves `test_metadata.kwargs.to`.

```python
def _resolve_ref_to_node_id(ref_str: str, manifest_nodes: dict) -> str | None:
    """Resolve ref('model_name') to a manifest node unique ID."""
    # Extract model name from ref string
    # Search manifest.nodes for matching node
    # Return node unique ID or None
```

**Relationship type:**

Use node/column `meta.relationship_type` if present (same pattern as test_relationship), defaulting to `"n1"` (many-to-one).

### Step 2: Create unit tests at `tests/unit/adapters/algos/test_model_contract.py`

Following the test pattern from `test_test_relationship.py` and `test_semantic.py`:

**Test fixtures needed in `tests/unit/adapters/algos/__init__.py`:**

Add new dummy manifest classes with constraint data:

```python
@dataclass
class ManifestNodeConstraint:
    type: ConstraintType  # enum or object with .value
    name: str | None = None
    expression: str | None = None
    to: str | None = None
    to_columns: list[str] | None = None
    columns: list[str] | None = None  # model-level only

@dataclass
class ManifestNodeColumnWithConstraints:
    name: str
    data_type: str = "unknown"
    description: str = ""
    constraints: list = field(default_factory=list)

@dataclass
class ManifestNodeWithConstraints:
    """Node with column-level FK constraints."""
    columns: dict  # ManifestNodeColumnWithConstraints
    constraints: list  # model-level constraints
    database: str = ""
    schema_: str = ""
    meta: dict = field(default_factory=dict)
    description: str = ""
    ...

@dataclass
class DummyManifestWithConstraints:
    nodes: ClassVar[dict] = {
        "model.pkg.orders": ManifestNodeWithConstraints(...),
        "model.pkg.customers": ManifestNodeWithConstraints(...),
    }
    sources: ClassVar[dict] = {}
```

**Test cases:**

1. `test_get_relationships` - happy path with column-level FK constraints
2. `test_get_relationships_model_level` - model-level FK constraints with `columns` field
3. `test_get_relationships_no_constraints` - nodes without constraints return empty
4. `test_get_relationships_non_fk_constraints_ignored` - primary_key, unique, not_null are skipped
5. `test_get_relationships_missing_to_field` - FK without `to` is skipped (pre-v12)
6. `test_get_relationships_self_referential` - FK pointing to same model
7. `test_get_relationships_with_relationship_type` - meta.relationship_type is respected
8. `test_parse_artifacts` - end-to-end mock test (file-based artifacts)
9. `test_find_related_nodes_by_id` - related node discovery
10. `test_resolve_ref_to_node_id` - ref string resolution edge cases
11. `test_manifest_without_constraints_attr` - graceful handling of older manifests

### Step 3: Create a sample project at `samples/model-contract/`

Create `manifest.json` and `catalog.json` with constraint data for integration testing:

- 2-3 models with foreign key constraints using `ref()`
- Mix of column-level and model-level constraints
- Include non-FK constraints to verify they're ignored

### Step 4: Add integration test

Add a new parametrized case to `tests/integration/test_dbterd_run.py`:

```python
("model-contract", "dbml", "model_contract", [], "output.dbml"),
```

With expected output in `tests/integration/expected_outputs/model-contract/output.dbml`.

### Step 5: Update documentation

- `docs/nav/guide/choose-algo.md` - add `model_contract` algorithm description
- Update any CLI help text or README sections listing available algorithms

---

## Files to Create

| File | Purpose |
|---|---|
| `dbterd/adapters/algos/model_contract.py` | Algorithm adapter |
| `tests/unit/adapters/algos/test_model_contract.py` | Unit tests |
| `samples/model-contract/manifest.json` | Sample manifest with constraints |
| `samples/model-contract/catalog.json` | Sample catalog |
| `tests/integration/expected_outputs/model-contract/output.dbml` | Expected integration output |

## Files to Modify

| File | Change |
|---|---|
| `tests/unit/adapters/algos/__init__.py` | Add dummy manifest classes with constraints |
| `tests/integration/test_dbterd_run.py` | Add model-contract integration test case |
| `docs/nav/guide/choose-algo.md` | Document the new algorithm |

## Files for Reference Only (do not modify)

| File | Why |
|---|---|
| `dbterd/adapters/algos/test_relationship.py` | Pattern to follow for algo adapter |
| `dbterd/adapters/algos/semantic.py` | Pattern to follow for algo adapter |
| `dbterd/core/adapters/algo.py` | Base class with shared methods |
| `dbterd/core/models.py` | `Ref`, `Table`, `Column` dataclasses |
| `dbterd/core/registry/decorators.py` | `@register_algo` decorator |
| `dbterd/core/executor.py` | Auto-discovers algo modules via `_register_adapters()` |
| `dbterd/types.py` | `Manifest` union type |
| `dbterd/constants.py` | Shared constants |

---

## Edge Cases & Known Limitations

1. **Manifest v1-v11**: No `to`/`to_columns` fields on constraints. Use `hasattr` checks; log a warning and return zero relationships. Don't attempt expression parsing.
2. **Manifest v12 non-model nodes**: Only `Nodes4` (model) has constraints. Seeds (`Nodes`), snapshots (`Nodes7`), and other node types lack constraint fields entirely. Only scan `model.*` prefixed nodes.
3. **`to` without `to_columns`**: FK has a target model but no target columns specified. Use the `from` column name as fallback (dbt allows this for same-named columns).
4. **Model-level constraints without `columns`**: Skip (can't determine which column is the FK). `Constraint5.columns` is `Optional[List[str]]`.
5. **Multiple FK columns (composite keys)**: A single model-level constraint may reference multiple columns. Create one `Ref` per column pair (matching positional order of `constraint.columns` and `constraint.to_columns`).
6. **Sources**: dbt constraints are only for models (not sources). Sources are included as tables but won't produce FK constraints.
7. **Non-FK constraint types**: `primary_key`, `unique`, `not_null`, `check`, `custom` are ignored for relationship extraction (they don't define inter-table links). Filter on `constraint.type.value == "foreign_key"`.
8. **dbt Cloud metadata API**: Out of scope. `parse_metadata()` is abstract in `BaseAlgoAdapter` and must be implemented -- log a warning and return `([], [])`. Can be added in a future iteration if/when the metadata API exposes constraint data.
9. **`constraint.to` format**: The `to` field in manifest v12 contains a ref string like `ref('model_name')` or `ref('package', 'model_name')`. Must parse this to match against manifest node keys. Reuse the same ref-parsing approach from `test_relationship.py`'s `get_table_map()`.
10. **Constraint type enum**: The `type` field is an enum (`Type` with values like `Type.foreign_key`). Access via `constraint.type.value` for string comparison.

---

## Test Plan

All tests target dbt Core (file-based artifacts) only. Run with `uv run coverage run -m pytest tests/unit && uv run coverage report --show-missing` to verify 100% coverage.

### Unit Tests: `tests/unit/adapters/algos/test_model_contract.py`

#### Test fixtures (`tests/unit/adapters/algos/__init__.py`)

New dummy classes to add:

| Class | Purpose |
|---|---|
| `ConstraintType` | Dataclass with `value: str` to mimic the `Type` enum |
| `ManifestNodeConstraint` | Dataclass mirroring `Constraint4`/`Constraint5` fields: `type`, `name`, `expression`, `to`, `to_columns`, `columns` (model-level only) |
| `ManifestNodeColumnWithConstraints` | Extends `ManifestNodeColumn` with `constraints: list` and `meta: dict` |
| `ManifestNodeWithConstraints` | Like `ManifestNode` but with `constraints: list` (model-level) and columns that are `ManifestNodeColumnWithConstraints` |
| `DummyManifestWithConstraints` | Manifest with `model.*` nodes containing FK constraints between tables |
| `DummyManifestWithModelLevelConstraints` | Manifest with model-level `Constraint5` (has `columns` field) |
| `DummyManifestNoConstraints` | Manifest with `model.*` nodes that have no `constraints` attr (simulates v1-v11) |

#### Test class: `TestAlgoModelContract`

##### `_resolve_ref_to_node_id` helper

| # | Test | Input | Expected |
|---|---|---|---|
| 1 | `test_resolve_ref_single_arg` | `ref_str="ref('customers')"`, nodes contain `model.pkg.customers` | `"model.pkg.customers"` |
| 2 | `test_resolve_ref_double_arg` | `ref_str="ref('pkg', 'customers')"`, nodes contain `model.pkg.customers` | `"model.pkg.customers"` |
| 3 | `test_resolve_ref_double_quotes` | `ref_str='ref("customers")'` | `"model.pkg.customers"` |
| 4 | `test_resolve_ref_not_found` | `ref_str="ref('nonexistent')"` | `None` |
| 5 | `test_resolve_ref_empty_string` | `ref_str=""` | `None` |

##### `get_relationships` (column-level constraints)

| # | Test | Scenario | Expected |
|---|---|---|---|
| 6 | `test_get_relationships_column_level_fk` | `orders.customer_id` has FK to `ref('customers')` with `to_columns=["id"]` | 1 `Ref` with `table_map=["model.pkg.customers", "model.pkg.orders"]`, `column_map=["id", "customer_id"]` |
| 7 | `test_get_relationships_multiple_fks` | `orders` has FKs on both `customer_id` and `product_id` | 2 `Ref` objects |
| 8 | `test_get_relationships_fk_without_to_columns` | FK constraint has `to` but `to_columns=None` | Falls back to `from_column` name as `to_column` |
| 9 | `test_get_relationships_self_referential` | `employee.manager_id` FK to `ref('employee')` | `Ref` with `table_map=["model.pkg.employee", "model.pkg.employee"]` |
| 10 | `test_get_relationships_with_relationship_type` | Column `meta={"relationship_type": "one-to-one"}` | `Ref` with `type="11"` |
| 11 | `test_get_relationships_non_fk_ignored` | Column has `primary_key`, `unique`, `not_null` constraints | Empty `[]` |
| 12 | `test_get_relationships_fk_without_to` | FK constraint has `to=None` (pre-v12 manifest) | Empty `[]` |
| 13 | `test_get_relationships_no_constraints_attr` | Node columns lack `constraints` attribute (v1-v8) | Empty `[]` |
| 14 | `test_get_relationships_empty_manifest` | `manifest.nodes = {}` | Empty `[]` |
| 15 | `test_get_relationships_skips_non_model_nodes` | Manifest contains `seed.*` and `test.*` nodes with no constraint attrs | Empty `[]` (only `model.*` scanned) |
| 16 | `test_get_relationships_unresolvable_ref` | FK `to="ref('deleted_model')"` doesn't match any node | Skipped, no `Ref` produced |
| 17 | `test_get_relationships_deduplication` | Two columns with identical FK constraint (same table_map + column_map) | 1 `Ref` (deduplicated via `get_unique_refs`) |

##### `get_relationships` (model-level constraints)

| # | Test | Scenario | Expected |
|---|---|---|---|
| 18 | `test_get_relationships_model_level_fk` | Node-level FK with `columns=["customer_id"]`, `to="ref('customers')"`, `to_columns=["id"]` | 1 `Ref` |
| 19 | `test_get_relationships_model_level_composite_fk` | Node-level FK with `columns=["org_id", "dept_id"]`, `to_columns=["id", "id"]` | 2 `Ref` objects (one per column pair) |
| 20 | `test_get_relationships_model_level_fk_no_columns` | Node-level FK with `columns=None` | Skipped, empty `[]` |
| 21 | `test_get_relationships_model_level_fk_no_to_columns` | Model FK with `columns=["customer_id"]`, `to_columns=None` | Falls back: `to_column` = `from_column` name |

##### `parse_artifacts`

| # | Test | Scenario | Expected |
|---|---|---|---|
| 22 | `test_parse_artifacts` | Mock `get_tables` and `get_relationships`; verify orchestration | Both called once; returns sorted `(tables, refs)` |
| 23 | `test_parse_artifacts_with_selection` | Pass `select` and `exclude` kwargs | `filter_tables_based_on_selection` applied |

##### `parse_metadata`

| # | Test | Scenario | Expected |
|---|---|---|---|
| 24 | `test_parse_metadata_not_supported` | Call `parse_metadata(data=[], ...)` | Returns `([], [])` with warning logged |

##### `find_related_nodes_by_id`

| # | Test | Scenario | Expected |
|---|---|---|---|
| 25 | `test_find_related_nodes_by_id_fk_source` | Node has FK to another model | Returns `[node_id, fk_target_id]` |
| 26 | `test_find_related_nodes_by_id_fk_target` | Another node has FK pointing to this node | Returns `[node_id, fk_source_id]` |
| 27 | `test_find_related_nodes_by_id_no_match` | Node has no FK relationships | Returns `[node_id]` |
| 28 | `test_find_related_nodes_by_id_metadata_type` | `type="metadata"` | Returns `[node_id]` (unsupported, passthrough) |

### Integration Test: `tests/integration/test_dbterd_run.py`

| # | Test | Sample | Target | Algo | Expected |
|---|---|---|---|---|---|
| 29 | `test_run_and_compare_output` (new parametrized case) | `model-contract` | `dbml` | `model_contract` | `output.dbml` matches expected |

**Sample artifacts** (`samples/model-contract/`):
- `manifest.json`: 3 models (`customers`, `orders`, `products`) where `orders` has column-level FK constraints pointing to `customers` and `products` via `ref()`. Include `not_null` and `primary_key` constraints on other columns to verify they're ignored.
- `catalog.json`: Matching catalog with column types.
- Expected output: `tests/integration/expected_outputs/model-contract/output.dbml` with 2 relationships.

### Coverage Requirements

- Target: **100%** line coverage on `dbterd/adapters/algos/model_contract.py`
- All branches covered: `hasattr` guards, `constraint.to is None`, `to_columns is None`, model-level `columns is None`, non-FK type filtering, empty manifest, unresolvable ref
- Verify with: `uv run coverage run -m pytest tests/unit && uv run coverage report --show-missing`
- Lint clean: `uv run ruff check . && uv run ruff format --check .`

---

## Usage

```bash
dbt docs generate
dbterd run --algo model_contract
```

Expected output:
```
2026-03-16 ... - dbterd - INFO - Using algorithm [model_contract]
2026-03-16 ... - dbterd - INFO - Using dbt artifact dir at: ...
2026-03-16 ... - dbterd - INFO - Collected X table(s) and Y relationship(s)
2026-03-16 ... - dbterd - INFO - Output saved to .../output.dbml
```
