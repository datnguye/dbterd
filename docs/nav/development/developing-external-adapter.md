# Developing an External Adapter

So you've built a custom algorithm or target adapter and you'd rather keep it in its own package than fork `dbterd`? Good news — `dbterd` supports **external adapter plugins** via Python entry points. Ship your adapter as a separate Python package — private or public — and `dbterd` will pick it up automatically at runtime. No pull request required (though we'd love one if it's useful to others).

!!! note "No PyPI required"
    Your external adapter does **not** need to be published to PyPI. Any installation method that registers the package in the environment works:

    - **Local editable install**: `pip install -e ./my-adapter`
    - **Git URL**: `pip install git+https://github.com/your-org/my-adapter.git`
    - **Private registry**: `pip install my-adapter --index-url https://your-registry/simple`
    - **Wheel / sdist file**: `pip install ./dist/my_adapter-0.1.0.tar.gz`

    As long as the package metadata (with `[project.entry-points]`) is installed in the same environment as `dbterd`, the entry points are discovered.

## How It Works

When `dbterd` starts, it discovers adapters from two sources:

1. **Built-in adapters** under `dbterd/adapters/algos/` and `dbterd/adapters/targets/`
2. **External packages** that declare entry points in the `dbterd.adapters` group

The discovery flow looks like this:

```
dbterd starts
    │
    ├── Scan built-in adapter modules
    │   └── import dbterd.adapters.algos.*
    │   └── import dbterd.adapters.targets.*
    │
    └── Scan entry points in "dbterd.adapters" group
        └── Load each entry point module
            └── @register_algo / @register_target decorators fire
                └── Adapter registered in PluginRegistry
```

Your external module just needs to be **imported** — the `@register_algo` or `@register_target` decorator handles the actual registration. Think of the entry point as a doorbell: `dbterd` rings it, your module wakes up, and the decorator announces itself to the registry.

## Quick Start

If you're the impatient type (no judgment), here's the shortest path to a working external adapter:

```bash
mkdir dbterd-target-myformat
cd dbterd-target-myformat
```

Create `pyproject.toml`:

```toml
[project]
name = "dbterd-target-myformat"
version = "0.1.0"
dependencies = ["dbterd"]

[project.entry-points."dbterd.adapters"]
myformat = "dbterd_target_myformat.adapter"
```

Create `dbterd_target_myformat/adapter.py`:

```python
"""External target adapter for dbterd."""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("myformat", description="My custom ERD format")
class MyFormatAdapter(BaseTargetAdapter):
    file_extension = ".myext"
    default_filename = "output.myext"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "?--", "11": "---", "0n": "?--<", "1n": "---<", "nn": ">--<",
    }
    DEFAULT_SYMBOL = ">--"

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        lines = [self.format_table(t, **kwargs) for t in tables]
        lines += [self.format_relationship(r, **kwargs) for r in relationships]
        return "\n".join(lines)

    def format_table(self, table: Table, **kwargs) -> str:
        return f"TABLE {table.name}"

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        symbol = self.get_rel_symbol(relationship.type)
        return f"{relationship.table_map[1]} {symbol} {relationship.table_map[0]}"
```

Install and run:

```bash
pip install -e .
dbterd run --target myformat
```

That's it. Your adapter is live.

## Project Structure

A typical external adapter package looks like:

```
dbterd-target-myformat/
├── pyproject.toml
├── dbterd_target_myformat/
│   ├── __init__.py
│   └── adapter.py          # Your adapter class with @register_target
└── tests/
    └── test_adapter.py
```

For an algorithm adapter, swap `target` for `algo`:

```
dbterd-algo-myalgo/
├── pyproject.toml
├── dbterd_algo_myalgo/
│   ├── __init__.py
│   └── adapter.py          # Your adapter class with @register_algo
└── tests/
    └── test_adapter.py
```

## Step-by-Step Guide

### 1. Create Your Package

Initialize a standard Python package. Use whatever build system you prefer — the entry point specification is standardized across all of them.

```toml
[project]
name = "dbterd-target-myformat"
version = "0.1.0"
description = "MyFormat target adapter for dbterd"
requires-python = ">=3.10"
dependencies = ["dbterd"]

[project.entry-points."dbterd.adapters"]
myformat = "dbterd_target_myformat.adapter"
```

### 2. Implement Your Adapter

Your adapter module must import and use the appropriate decorator. When `dbterd` loads the entry point, the module is imported, which triggers the decorator, which registers your adapter in the `PluginRegistry`.

For **target adapters**, inherit from `BaseTargetAdapter` and use `@register_target`:

```python
from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.registry.decorators import register_target

@register_target("myformat", description="My custom format")
class MyFormatAdapter(BaseTargetAdapter):
    ...
```

For **algorithm adapters**, inherit from `BaseAlgoAdapter` and use `@register_algo`:

```python
from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.registry.decorators import register_algo

@register_algo("my_algo", description="My custom relationship detection")
class MyAlgoAdapter(BaseAlgoAdapter):
    ...
```

See [Developing a Target Adapter](developing-target-adapter.md) and [Developing an Algorithm Adapter](developing-algo-adapter.md) for the full implementation details on each adapter type.

### 3. Register the Entry Point

The entry point name (left side of `=`) is an identifier used for logging. The value (right side) must point to the **module** containing your decorated adapter class.

```toml
[project.entry-points."dbterd.adapters"]
myformat = "dbterd_target_myformat.adapter"
```

!!! info "Module, not class"
    The entry point should reference the **module**, not the class directly. The module import triggers the `@register_target` / `@register_algo` decorator, which is what performs the actual registration. Pointing at the class works too (`dbterd_target_myformat.adapter:MyFormatAdapter`), but it's unnecessary since the decorator fires on import either way.

You can register multiple adapters from a single package:

```toml
[project.entry-points."dbterd.adapters"]
myformat = "my_package.targets.myformat"
my_algo = "my_package.algos.my_algo"
```

### 4. Install and Verify

Install your package (editable mode is handy during development):

```bash
pip install -e .
```

Verify that `dbterd` sees your adapter:

```bash
# For target adapters
dbterd run --target myformat --help

# For algorithm adapters
dbterd run --algo my_algo --help
```

If the adapter loaded successfully, `dbterd` will accept it as a valid option. If it failed to load, you'll see a warning in the logs:

```
WARNING - Failed to load external adapter entry point 'myformat'
```

## Complete Example: External Target Adapter

Here's a full working example of an external target adapter that generates a CSV-based ERD format — because sometimes you just want to throw your relationships into a spreadsheet.

**`pyproject.toml`**:

```toml
[project]
name = "dbterd-target-csv"
version = "0.1.0"
description = "CSV target adapter for dbterd"
requires-python = ">=3.10"
dependencies = ["dbterd"]

[project.entry-points."dbterd.adapters"]
csv = "dbterd_target_csv.adapter"
```

**`dbterd_target_csv/adapter.py`**:

```python
"""CSV target adapter for dbterd.

Generates ERD data in CSV format for spreadsheet-friendly consumption.
"""

from typing import ClassVar

from dbterd.core.adapters.target import BaseTargetAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_target


@register_target("csv", description="CSV format for spreadsheet tools")
class CsvAdapter(BaseTargetAdapter):
    """CSV target adapter."""

    file_extension = ".csv"
    default_filename = "erd.csv"

    RELATIONSHIP_SYMBOLS: ClassVar[dict[str, str]] = {
        "01": "zero-to-one",
        "11": "one-to-one",
        "0n": "zero-to-many",
        "1n": "one-to-many",
        "nn": "many-to-many",
    }
    DEFAULT_SYMBOL = "many-to-one"

    def build_erd(self, tables: list[Table], relationships: list[Ref], **kwargs) -> str:
        """Build CSV ERD content."""
        lines = ["from_table,from_column,relationship,to_table,to_column"]

        for rel in relationships:
            lines.append(self.format_relationship(rel, **kwargs))

        return "\n".join(lines)

    def format_table(self, table: Table, **kwargs) -> str:
        """Format a single table (not used in CSV output)."""
        return table.name

    def format_relationship(self, relationship: Ref, **kwargs) -> str:
        """Format a single relationship as a CSV row."""
        symbol = self.get_rel_symbol(relationship.type)
        return (
            f"{relationship.table_map[1]},"
            f"{relationship.column_map[1]},"
            f"{symbol},"
            f"{relationship.table_map[0]},"
            f"{relationship.column_map[0]}"
        )
```

Usage:

```bash
pip install -e .
dbterd run --target csv
```

## Complete Example: External Algorithm Adapter

An external algorithm adapter that detects relationships using dbt `meta` tags:

**`pyproject.toml`**:

```toml
[project]
name = "dbterd-algo-meta-refs"
version = "0.1.0"
description = "Meta-based relationship detection for dbterd"
requires-python = ">=3.10"
dependencies = ["dbterd"]

[project.entry-points."dbterd.adapters"]
meta_refs = "dbterd_algo_meta_refs.adapter"
```

**`dbterd_algo_meta_refs/adapter.py`**:

```python
"""Meta-based relationship detection algorithm for dbterd.

Detects relationships using custom meta tags on dbt columns:
    columns:
      - name: user_id
        meta:
          references:
            table: users
            column: id
            type: n1
"""

from dbterd.core.adapters.algo import BaseAlgoAdapter
from dbterd.core.models import Ref, Table
from dbterd.core.registry.decorators import register_algo
from dbterd.helpers.log import logger
from dbterd.types import Catalog, Manifest


@register_algo("meta_refs", description="Detect relationships via column meta tags")
class MetaRefsAlgo(BaseAlgoAdapter):
    """Algorithm adapter using dbt column meta tags."""

    def parse_artifacts(
        self, manifest: Manifest, catalog: Catalog, **kwargs
    ) -> tuple[list[Table], list[Ref]]:
        """Parse from file-based manifest/catalog artifacts."""
        tables = self.get_tables(manifest=manifest, catalog=catalog, **kwargs)
        tables = self.filter_tables_based_on_selection(tables=tables, **kwargs)

        relationships = self._get_meta_relationships(manifest=manifest)
        relationships = self.make_up_relationships(
            relationships=relationships, tables=tables
        )

        logger.info(
            f"Collected {len(tables)} table(s) and {len(relationships)} relationship(s)"
        )
        return (
            sorted(tables, key=lambda tbl: tbl.node_name),
            sorted(relationships, key=lambda rel: rel.name),
        )

    def parse_metadata(self, data: dict, **kwargs) -> tuple[list[Table], list[Ref]]:
        """Parse from dbt Cloud metadata API response."""
        raise NotImplementedError("Metadata API not supported by meta_refs algorithm")

    def _get_meta_relationships(self, manifest: Manifest) -> list[Ref]:
        """Extract relationships from column meta tags."""
        refs = []
        for node_id, node in manifest.nodes.items():
            if not node_id.startswith("model."):
                continue
            for col_name, col in node.columns.items():
                meta_ref = col.meta.get("references") if col.meta else None
                if not meta_ref:
                    continue

                target_table = meta_ref.get("table")
                target_column = meta_ref.get("column", "id")
                rel_type = meta_ref.get("type", "n1")

                # Find the target node by table name
                target_node_id = self._resolve_node(manifest, target_table)
                if not target_node_id:
                    logger.debug(f"Could not resolve target table '{target_table}'")
                    continue

                refs.append(
                    Ref(
                        name=f"meta.{node_id}.{col_name}",
                        table_map=(target_node_id, node_id),
                        column_map=(target_column, col_name),
                        type=rel_type,
                    )
                )

        return self.get_unique_refs(refs=refs)

    def _resolve_node(self, manifest: Manifest, table_name: str) -> str | None:
        """Resolve a table name to a full node ID."""
        for node_id in manifest.nodes:
            if node_id.endswith(f".{table_name}"):
                return node_id
        return None
```

Usage:

```bash
pip install -e .
dbterd run --algo meta_refs
```

## Testing Your Plugin

You can test your external adapter independently, without needing to install `dbterd` from source. The key is to mock the parts you don't control and test your logic directly:

```python
"""Tests for external adapter plugin."""

import pytest

from dbterd.core.models import Column, Ref, Table


@pytest.fixture
def sample_table():
    return Table(
        name="orders",
        database="analytics",
        schema="public",
        columns=[
            Column(name="id", data_type="integer"),
            Column(name="user_id", data_type="integer"),
        ],
        node_name="model.shop.orders",
    )


@pytest.fixture
def sample_ref():
    return Ref(
        name="test.ref",
        table_map=("model.shop.users", "model.shop.orders"),
        column_map=("id", "user_id"),
        type="n1",
    )


class TestMyAdapter:
    def test_format_relationship(self, sample_ref):
        from dbterd_target_myformat.adapter import MyFormatAdapter

        adapter = MyFormatAdapter()
        result = adapter.format_relationship(sample_ref)
        assert "model.shop.orders" in result
        assert "model.shop.users" in result

    def test_build_erd(self, sample_table, sample_ref):
        from dbterd_target_myformat.adapter import MyFormatAdapter

        adapter = MyFormatAdapter()
        result = adapter.build_erd([sample_table], [sample_ref])
        assert "orders" in result
```

To verify entry point registration end-to-end:

```python
def test_entry_point_registered():
    """Verify the adapter registers via entry point."""
    from importlib.metadata import entry_points

    eps = entry_points(group="dbterd.adapters")
    names = [ep.name for ep in eps]
    assert "myformat" in names
```

## Distribution

Your adapter works with any standard Python installation method. Pick whatever fits your workflow:

### Private / Internal Use

For team-internal or private adapters, just install directly from source:

```bash
# Editable install from local path (great for development)
pip install -e ./my-adapter

# Install from a private Git repo
pip install git+https://github.com/your-org/my-adapter.git

# Install from a private PyPI registry
pip install my-adapter --index-url https://your-registry/simple

# Install from a built wheel or sdist
pip install ./dist/my_adapter-0.1.0.tar.gz
```

### Publishing to PyPI

When your adapter is ready for the world:

1. **Choose a clear name** — follow the convention `dbterd-target-<name>` or `dbterd-algo-<name>` so users can find it easily.

2. **Pin your dbterd dependency** — use a compatible release specifier to avoid breaking on major versions:

    ```toml
    dependencies = ["dbterd>=0.5,<1.0"]
    ```

3. **Build and publish**:

    ```bash
    pip install build twine
    python -m build
    twine upload dist/*
    ```

4. **Users install it alongside dbterd**:

    ```bash
    pip install dbterd dbterd-target-myformat
    dbterd run --target myformat
    ```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `WARNING - Failed to load external adapter entry point 'xxx'` | Import error in your module | Run `python -c "import your_module.adapter"` to see the full traceback |
| Adapter not recognized as a valid option | Entry point not installed | Run `pip show your-package` and check the entry points are listed |
| `ModuleNotFoundError: No module named 'dbterd'` | `dbterd` not in your dependencies | Add `dbterd` to `[project.dependencies]` |
| Adapter works in dev but not after install | Entry point module path is wrong | Double-check the dotted path matches your package layout |

!!! tip "Debug entry point discovery"
    You can list all registered entry points from Python to verify your adapter is visible:

    ```python
    from importlib.metadata import entry_points

    for ep in entry_points(group="dbterd.adapters"):
        print(f"{ep.name} = {ep.value}")
    ```

## Tips and Best Practices

1. **Keep `dbterd` as a dependency, not a devDependency** — your adapter imports from `dbterd` at runtime, so it needs to be a real dependency.

2. **Don't duplicate adapter names** — if you register a name that conflicts with a built-in adapter, behavior is undefined. Pick a unique name.

3. **Fail gracefully** — if your adapter has optional heavy dependencies (like a database driver), catch the import error and provide a helpful message instead of crashing `dbterd`.

4. **Follow the naming convention** — `dbterd-target-*` for targets, `dbterd-algo-*` for algorithms. This keeps things discoverable whether your package is internal or public.

5. **Test against multiple dbterd versions** — entry points are stable, but the base classes may evolve. CI matrix testing saves you from surprise breakage.

6. **Read the existing adapter guides** — [Developing a Target Adapter](developing-target-adapter.md) and [Developing an Algorithm Adapter](developing-algo-adapter.md) cover the full adapter API in detail. This guide focuses on the external packaging and discovery mechanism.
