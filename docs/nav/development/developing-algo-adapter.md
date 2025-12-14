# Developing an Algorithm Adapter

Want to teach `dbterd` a new trick for sniffing out relationships in your dbt project? Perhaps you've got a clever way to detect foreign keys using naming conventions, or maybe you want to leverage some metadata that the existing algorithms don't understand. Welcome to the algorithm adapter development guide!

## What is an Algorithm Adapter?

An algorithm adapter is responsible for parsing dbt artifacts (manifest and catalog) to extract **tables** and **relationships**. Different algorithms use different strategies to discover how tables are connected:

- **test_relationship** - Uses dbt's `relationships` test to find foreign keys
- **semantic** - Uses dbt's Semantic Layer entities (primary/foreign) to determine connections

Your custom algorithm might detect relationships through naming conventions (e.g., `*_id` columns), comments, tags, or any other creative method you can dream up.

## Quick Start

Here's the minimal skeleton:

```python
"""My relationship detection algorithm for dbterd."""

from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


@register_algo("my_algo", description="Detect relationships using my clever method")
class MyAlgo(BaseAlgoAdapter):
    """My custom algorithm adapter."""

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        # Extract tables using inherited helper
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        # Extract relationships using YOUR logic
        relationships = self.get_relationships(manifest=manifest, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from dbt Cloud metadata API response."""
        # Implement if you want to support dbt Cloud metadata
        raise NotImplementedError("Metadata API not supported yet")

    def get_relationships(self, manifest: Manifest, **kwargs) -> list[Ref]:
        """Your custom relationship detection logic."""
        refs = []
        # Your magic here!
        return refs
```

## The Base Class

Your adapter must inherit from `BaseAlgoAdapter` which provides:

| Method | Type | Description |
|--------|------|-------------|
| `parse()` | method | Entry point - dispatches to `parse_artifacts()` or `parse_metadata()` |
| `parse_artifacts()` | abstract | **You implement this** - parse file-based artifacts |
| `parse_metadata()` | abstract | **You implement this** - parse dbt Cloud metadata API |
| `get_tables()` | inherited | Extracts tables from manifest/catalog |
| `get_tables_from_metadata()` | inherited | Extracts tables from metadata API |
| `filter_tables_based_on_selection()` | inherited | Filters tables by selection rules |
| `make_up_relationships()` | inherited | Filters refs and applies entity name format |
| `get_unique_refs()` | inherited | Deduplicates relationships |
| `enrich_tables_from_relationships()` | inherited | Adds missing columns from relationships |
| `find_related_nodes_by_id()` | virtual | Override to support single-model ERDs |

## Step-by-Step Guide

### 1. Create Your Adapter File

Create a new file in `dbterd/adapters/algos/`:

```bash
touch dbterd/adapters/algos/my_algo.py
```

### 2. Implement the Required Methods

**`parse_artifacts()`** - The main workhorse for file-based artifacts:

```python
def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
    """Parse tables and relationships from dbt artifacts."""
    # Step 1: Get all tables (the base class does the heavy lifting)
    tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)

    # Step 2: Apply selection filters (--select, --exclude)
    tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

    # Step 3: Get relationships using YOUR detection method
    relationships = self.get_relationships(manifest=manifest, **kwargs)

    # Step 4: Filter relationships to only include selected tables
    # and apply entity_name_format to table names
    relationships = self.make_up_relationships(relationships=relationships, tables=tables)

    # Step 5: (Optional) Add columns discovered from relationships
    tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

    logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")

    # Return sorted for deterministic output
    return (
        sorted(tables, key=lambda tbl: tbl.node_name),
        sorted(relationships, key=lambda rel: rel.name),
    )
```

**`parse_metadata()`** - For dbt Cloud metadata API support:

```python
def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
    """Parse from dbt Cloud metadata API response."""
    data_list = data if isinstance(data, list) else [data]

    # Get tables from metadata
    tables = self.get_tables_from_metadata(data=data_list, **kwargs)
    tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

    # Get relationships from metadata (implement your logic)
    relationships = self.get_relationships_from_metadata(data=data_list, **kwargs)
    relationships = self.make_up_relationships(relationships=relationships, tables=tables)

    logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
    return (
        sorted(tables, key=lambda tbl: tbl.node_name),
        sorted(relationships, key=lambda rel: rel.name),
    )
```

### 3. Register Your Algorithm

The `@register_algo` decorator automatically registers your adapter:

```python
@register_algo("my_algo", description="Detect relationships using naming conventions")
class MyAlgo(BaseAlgoAdapter):
    ...
```

Users can then use it via CLI:

```bash
dbterd run --algo my_algo
```

## Understanding the Data Flow

```
┌─────────────────┐     ┌─────────────────┐
│   manifest.json │     │   catalog.json  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Your Algorithm      │
         │   parse_artifacts()   │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  list[Table]    │     │  list[Ref]      │
│                 │     │                 │
│  - name         │     │  - name         │
│  - columns      │     │  - table_map    │
│  - database     │     │  - column_map   │
│  - schema       │     │  - type         │
│  - ...          │     │  - ...          │
└─────────────────┘     └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Target Adapter      │
         │   (DBML, Mermaid...)  │
         └───────────────────────┘
```

## Working with Manifest and Catalog

### Manifest Structure

The manifest is a typed object with these key attributes:

```python
manifest.nodes          # Dict of models, tests, seeds, snapshots
manifest.sources        # Dict of source definitions
manifest.exposures      # Dict of exposures
manifest.semantic_models  # Dict of semantic models (dbt 1.6+)
```

Each node has properties like:

```python
node = manifest.nodes["model.my_project.users"]
node.name              # "users"
node.database          # "analytics"
node.schema_           # "public" (note the underscore!)
node.columns           # Dict of column metadata
node.depends_on.nodes  # List of upstream dependencies
node.meta              # Custom metadata dict
node.description       # Model description
```

### Catalog Structure

The catalog contains runtime information:

```python
catalog.nodes           # Dict with column types from the actual database
catalog.sources         # Source column information
```

Each catalog node has:

```python
catalog_node = catalog.nodes["model.my_project.users"]
catalog_node.columns    # Dict with actual column types
# catalog_node.columns["id"].type  -> "INTEGER"
```

## Inherited Helper Methods

### Table Extraction

You typically don't need to reimplement table extraction - just use the inherited methods:

```python
# For file-based artifacts
tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)

# For metadata API
tables = self.get_tables_from_metadata(data=data_list, **kwargs)

# Filter by --select and --exclude
tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)
```

The `entity_name_format` kwarg controls table naming:

- `resource.package.model` → `model.jaffle_shop.orders`
- `schema.model` → `public.orders`
- `database.schema.table` → `analytics.public.orders`

### Relationship Processing

After you create your `Ref` objects, use these helpers:

```python
# Remove duplicates
refs = self.get_unique_refs(refs=refs)

# Filter to selected tables and apply entity_name_format
relationships = self.make_up_relationships(relationships=refs, tables=tables)

# Add missing columns discovered from relationships
tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)
```

## Complete Example

Here's a complete algorithm that detects relationships based on `*_id` naming conventions:

```python
"""Naming convention algorithm adapter for dbterd.

Detects relationships by matching column names ending in '_id'
to primary key columns in other tables.
"""

from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


@register_algo("naming_convention", description="Detect relationships via *_id naming patterns")
class NamingConventionAlgo(BaseAlgoAdapter):
    """Algorithm adapter using naming conventions.

    Finds relationships by matching columns ending in '_id' to
    tables with matching names (e.g., user_id -> users.id).
    """

    def parse_artifacts(self, manifest: Manifest, catalog: Catalog, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        relationships = self.get_relationships(tables=tables, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        tables = self.enrich_tables_from_relationships(tables=tables, relationships=relationships)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from dbt Cloud metadata API response."""
        data_list = data if isinstance(data, list) else [data]

        tables = self.get_tables_from_metadata(data=data_list, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        relationships = self.get_relationships(tables=tables, **kwargs)
        relationships = self.make_up_relationships(relationships=relationships, tables=tables)

        logger.info(f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)")
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def get_relationships(self, tables: list[Table], **kwargs) -> list[Ref]:
        """Detect relationships based on naming conventions.

        Looks for columns ending in '_id' and matches them to tables
        with the corresponding singular name.

        Args:
            tables: List of parsed tables
            **kwargs: Additional options

        Returns:
            List of detected relationships
        """
        refs = []
        table_names = {t.node_name.split(".")[-1].lower(): t for t in tables}

        for table in tables:
            for column in table.columns:
                col_name = column.name.lower()

                # Check if column ends with '_id'
                if not col_name.endswith("_id"):
                    continue

                # Skip 'id' column itself
                if col_name == "id":
                    continue

                # Try to find the referenced table
                # e.g., user_id -> users, order_id -> orders
                base_name = col_name[:-3]  # Remove '_id'
                possible_tables = [
                    base_name,           # user
                    f"{base_name}s",     # users
                    f"{base_name}es",    # boxes
                ]

                for possible_name in possible_tables:
                    if possible_name in table_names:
                        target_table = table_names[possible_name]
                        refs.append(
                            Ref(
                                name=f"naming.{table.node_name}.{col_name}",
                                table_map=(target_table.node_name, table.node_name),
                                column_map=("id", col_name),
                                type="n1",  # many-to-one
                            )
                        )
                        logger.debug(
                            f"Found relationship: {table.node_name}.{col_name} -> {target_table.node_name}.id"
                        )
                        break

        return self.get_unique_refs(refs=refs)
```

## Supporting dbt Cloud Metadata API

If you want to support dbt Cloud's metadata API, implement `parse_metadata()`. The data structure is different from file-based artifacts:

```python
def get_relationships_from_metadata(self, data: list, **kwargs) -> list[Ref]:
    """Extract relationships from metadata API response."""
    refs = []

    for data_item in data:
        # Models are under data_item["models"]["edges"]
        for model in data_item.get("models", {}).get("edges", []):
            node = model.get("node", {})
            unique_id = node.get("uniqueId")
            # Your logic here...

    return self.get_unique_refs(refs=refs)
```

## Testing Your Adapter

Create tests in `tests/unit/adapters/algos/test_my_algo.py`:

```python
"""Tests for naming convention algorithm adapter."""

import pytest

from dbterd.adapters.algos.naming_convention import NamingConventionAlgo
from dbterd.core.models import Column, Table


@pytest.fixture
def algo():
    return NamingConventionAlgo()


@pytest.fixture
def sample_tables():
    return [
        Table(
            name="users",
            database="db",
            schema="public",
            columns=[Column(name="id", data_type="integer")],
            node_name="model.project.users",
        ),
        Table(
            name="orders",
            database="db",
            schema="public",
            columns=[
                Column(name="id", data_type="integer"),
                Column(name="user_id", data_type="integer"),
            ],
            node_name="model.project.orders",
        ),
    ]


class TestNamingConventionAlgo:
    def test_get_relationships_finds_user_id(self, algo, sample_tables):
        refs = algo.get_relationships(tables=sample_tables)

        assert len(refs) == 1
        assert refs[0].table_map == ("model.project.users", "model.project.orders")
        assert refs[0].column_map == ("id", "user_id")

    def test_get_relationships_ignores_id_column(self, algo):
        tables = [
            Table(
                name="items",
                database="db",
                schema="public",
                columns=[Column(name="id", data_type="integer")],
                node_name="model.project.items",
            ),
        ]
        refs = algo.get_relationships(tables=tables)
        assert len(refs) == 0
```

Run tests:

```bash
poe test tests/unit/adapters/algos/test_my_algo.py
```

## Tips and Best Practices

1. **Start with existing algorithms** - Study `test_relationship.py` and `semantic.py` to understand the patterns and edge cases.

2. **Use the inherited helpers** - Don't reinvent table extraction. Use `get_tables()` and focus your effort on relationship detection.

3. **Return node_name in table_map** - The `make_up_relationships()` helper expects full node names (e.g., `model.project.users`), not formatted names.

4. **Handle missing data gracefully** - Manifest and catalog may have incomplete information. Check for `None` and missing attributes.

5. **Log your discoveries** - Use `logger.debug()` to help users understand what relationships your algorithm found (and why).

6. **Support `find_related_nodes_by_id()`** - If you want to support single-model ERDs, override this method to find related tables:

    ```python
    def find_related_nodes_by_id(
        self,
        manifest: Manifest,
        node_unique_id: str,
        type: str | None = None,
        **kwargs,
    ) -> list[str]:
        """Find tables related to the given node."""
        found_nodes = [node_unique_id]
        # Add logic to find related nodes
        return list(set(found_nodes))
    ```

7. **Support relationship types** - If your detection method can determine cardinality, set the `type` field appropriately:
   - `"0n"` - zero-to-many
   - `"01"` - zero-to-one
   - `"11"` - one-to-one
   - `"nn"` - many-to-many
   - `"1n"` - one-to-many
   - `"n1"` - many-to-one (default)

8. **Document your algorithm** - Add a doc page in `docs/nav/guide/` explaining how to use your algorithm and what it detects.

Happy relationship hunting! 🔍
