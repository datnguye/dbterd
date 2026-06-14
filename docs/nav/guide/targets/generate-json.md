# Generate JSON

The `json` target emits dbterd's **canonical ERD payload** — a stable, schema-validated
shape (`nodes` / `edges` / `metadata`) designed to be consumed by other tools rather than
imported into a drawing app. It's the format the
[dbterd VS Code extension](https://github.com/datnguye/dbterd-vscode) speaks natively, so if
you're building an integration this is the target you want.

## 1. Produce dbt artifact files

Let's use [Jaffle-Shop](https://github.com/dbt-labs/jaffle-shop) as the example.

Clone it, then run `dbt docs generate` to produce the `/target` folder containing:

- `manifest.json`
- `catalog.json`

Or just use the generated files in the [samples](https://github.com/datnguye/dbterd/tree/main/samples/jaffle-shop).

## 2. Generate the JSON file

In the same dbt project directory, run `dbterd` to generate the `.json` file:

```bash
dbterd run -t json
```

Here is a trimmed sample of the output:

```json
{
  "$schema": "https://datnguye.github.io/dbterd/schemas/erd/latest/erd.json",
  "nodes": [
    {
      "id": "model.jaffle_shop.orders",
      "name": "orders",
      "label": null,
      "description": "One row per order.",
      "resource_type": "model",
      "schema_name": "analytics",
      "database": "prod",
      "columns": [
        {
          "name": "order_id",
          "data_type": "INT",
          "description": "The primary key.",
          "is_primary_key": true,
          "is_foreign_key": false
        }
      ],
      "compiled_sql": null
    }
  ],
  "edges": [
    {
      "id": "test.jaffle_shop.relationships_order_items_order_id",
      "from_id": "model.jaffle_shop.order_items",
      "to_id": "model.jaffle_shop.orders",
      "from_columns": ["order_id"],
      "to_columns": ["order_id"],
      "relationship_type": "fk",
      "name": "test.jaffle_shop.relationships_order_items_order_id",
      "label": null,
      "cardinality": "n1"
    }
  ],
  "metadata": {
    "generated_at": "2024-07-28T01:54:24.620460Z",
    "dbt_project_name": "jaffle_shop",
    "dbterd_version": "1.2.3"
  }
}
```

## 3. Validate against the schema

Every payload carries a `$schema` URL pinned to the dbterd version that produced it. The
schema is published on this site at
[`schemas/erd/latest/erd.json`](/dbterd/schemas/erd/latest/erd.json)
(versioned copies live at `schemas/erd/{version}/erd.json`), so you can validate output in CI:

```bash
# any draft 2020-12 validator works; example with check-jsonschema
pipx run check-jsonschema --schemafile \
  https://datnguye.github.io/dbterd/schemas/erd/latest/erd.json \
  output.json
```

## Field reference

| Object   | Field               | Notes                                                            |
| -------- | ------------------- | ---------------------------------------------------------------- |
| node     | `id`                | dbt unique id, e.g. `model.jaffle_shop.orders`                   |
| node     | `name`              | Friendly table name (respects `--entity-name-format`)           |
| node     | `resource_type`     | `model` / `source` / `seed` / `snapshot`                        |
| node     | `schema_name`       | dbt schema                                                       |
| node     | `database`          | dbt database                                                     |
| node     | `compiled_sql`      | Compiled SQL (falls back to raw dbt code); `null` when absent    |
| column   | `is_primary_key`    | True when the column is the model's primary key                  |
| column   | `is_foreign_key`    | Derived — true when the column participates in a relationship    |
| edge     | `from_id` / `to_id` | FK (child) side → referenced (parent) side                       |
| edge     | `from_columns`      | Full column list; supports composite foreign keys               |
| edge     | `cardinality`       | dbterd code: `n1`, `1n`, `11`, `nn`, `01`, `0n`                 |
| metadata | `generated_at`      | Manifest generation timestamp                                    |
| metadata | `dbterd_version`    | dbterd version that produced the payload (matches `$schema`)     |
