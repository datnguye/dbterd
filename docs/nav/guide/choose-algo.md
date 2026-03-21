# Choosing the algorithm (parsers) to parse the Entity Relationships (ERs)

There are 3 approaches (or 3 modules) we can use here to let `dbterd` look at how the ERs can be recognized between the dbt models:

1. **Test Relationship** ([docs](https://docs.getdbt.com/reference/resource-properties/data-tests#relationships), [source](https://github.com/datnguye/dbterd/blob/main/dbterd/adapters/algos/test_relationship.py)) (default)
2. **Semantic Entities** ([docs](https://docs.getdbt.com/docs/build/entities), [source](https://github.com/datnguye/dbterd/blob/main/dbterd/adapters/algos/semantic.py))
3. **Model Contract** ([docs](https://docs.getdbt.com/docs/collaborate/govern/model-contracts), [source](https://github.com/datnguye/dbterd/blob/main/dbterd/adapters/algos/model_contract.py))

## Test Relationship

During the dbt development, the engineers are supposed to add the consistency checking using `relationships` test function, or similarly specifying the dbt contraints (they're also the tests behind the scenes), given the below example project with [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop).

Let's install the repo:

```bash
git clone https://github.com/dbt-labs/jaffle-shop
cd jaffle-shop
```

Setup the environment, and install the deps including `dbterd`:

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
pip install dbterd --upgrade
```

In the `order_items.sql` model, we can see 1 sample test:

```yaml
models:
  - name: order_items
    columns:
      - name: order_item_id
        data_tests:
          - not_null
          - unique
      - name: order_id
        data_tests:
          - relationships: # dbterd looks for all kind of this test
              to: ref('orders')
              field: order_id
```

Running `dbterd run -enf table` will expose the DBML code as below:

```
Table "orders" {
...
}
Table "order_items" {
...
}
...
Ref: "order_items"."order_id" > "orders"."order_id"
...
```

Awesome, job done here 🎉

NO, not yet (maybe!), sometimes this module is not going to work perfectly due to:

- Some relationship tests are added from `mart` to `staging` just for ensuring no missing data when moving from a layer to another.
    - That's why we have the [ignore_in_erd](https://dbterd.datnguyen.de/1.15/nav/metadata/ignore_in_erd.html) metadata config.
- We have the tests done in separate tools already (e.g. Soda), there is no reason to duplicate the (relationship) tests here.
    - No problem! Let's still add it with `where: 1=0` or with the dummy relationship tests (see this [blogpost](https://medium.com/@vaibhavchopda04/generating-erds-from-dbt-projects-a-code-driven-approach-83abb957f483))

In case we don't want to leverage the dbt tests still, let's move on to the next section for the alternative 🏃

## Semantic Entities

Since dbt v1.6, dbt has supported the Semantic Layer (SL) with Metric Flow ([docs](https://docs.getdbt.com/docs/build/about-metricflow)), we have the ability to define entities in our semantic modelling, telling `metricflow` how to join tables together. Therefore, it now becomes the 2nd parser for our choice of usage if we have implemented the dbt SL already.

`dbterd` can now look for the Semantic [Entities](https://docs.getdbt.com/docs/build/entities) (`primary` and `foreign`) in order to understand the ERs, subsequently produce the ERD code.

Let's use the above [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop) project again, here is the sample code which was implemented in the repo for the semantic models: `order_item` and `orders`:

```yaml
semantic_models:
  - name: order_item
    ...
    model: ref('order_items')
    entities:
      - name: order_item
        type: primary
        expr: order_item_id
      - name: order_id
        type: foreign
        expr: order_id
  ...
  - name: orders
    ...
    model: ref('orders')
    entities:
      - name: order_id
        type: primary
```

Now running `dbterd run -enf table` with the environment variable `DBTERD_ALGO=semantic` in advance, or we can use the command without it :

```bash
dbterd run -enf table -a semantic
```

The result DBML code will be the same as the 1st option. Voila! 🎉🎉

## Model Contract

Since dbt v1.9, dbt supports enforcing [model contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts) with column-level and model-level constraints, including `foreign_key`. When a `foreign_key` constraint carries a `to` field pointing to another model, `dbterd` can read those declarations directly to infer relationships — no tests or semantic models required.

This algorithm requires **manifest v12+** (dbt 1.9+).

!!! warning "Contract must be enforced"
    The `foreign_key` constraint's `to` field is only populated in the manifest when `contract.enforced: true` is set on the model. Without enforcement, dbt will not write the FK target into the artifact and `dbterd` will find no relationships.

Run `dbterd` with the `model_contract` algorithm:

```bash
dbterd run -a model_contract
```

No duplicate test definitions needed — the contract itself is the source of truth.

### Column-level FK

Using the same [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop) project, here is a sample contract with a single-column foreign key from `orders` to `locations`:

```yaml
models:
  - name: orders
    config:
      contract:
        enforced: true
    columns:
      - name: location_id
        constraints:
          - type: foreign_key
            name: fk_order_to_location
            to: ref('locations')
            to_columns: [location_id]
```

The result will include the relationship inferred from the constraint:

```
Ref: "model.dbt_project.orders"."location_id" > "model.dbt_project.locations"."location_id"
```

### Model-level FK (composite relationships)

When a foreign key spans multiple columns, define it at the model level using `constraints`:

```yaml
models:
  - name: fct_customer_segment_orders
    config:
      contract:
        enforced: true
    constraints:
      - type: foreign_key
        name: fk_segment_order_to_customer_segment
        to: ref('dim_customer_segment')
        columns: [customer_id, segment_code]
        to_columns: [customer_id, segment_code]
```

The result will include the multi-column relationship:

```
Ref: "model.dbt_project.fct_customer_segment_orders".("customer_id", "segment_code") > "model.dbt_project.dim_customer_segment".("customer_id", "segment_code")
```

### Primary key detection

`dbterd` automatically marks columns as primary keys from `primary_key` constraints — both at the column level and the model level (for composite PKs).

**Column-level PK:**

```yaml
models:
  - name: orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        constraints:
          - type: primary_key
```

**Model-level composite PK:**

```yaml
models:
  - name: dim_customer_segment
    config:
      contract:
        enforced: true
    constraints:
      - type: primary_key
        columns: [customer_id, segment_code]
```

The affected columns will appear with a `[pk]` index in the ERD output.

### Relationship labels

!!! note
    Relationship labels are only rendered in the **Mermaid** target. Other output formats ignore this field.

To annotate a relationship edge with a label, add a `relationship_labels` dict to the model's `meta`, keyed by the constraint name:

```yaml
models:
  - name: orders
    meta:
      relationship_labels:
        fk_order_to_location: order_to_location
    config:
      contract:
        enforced: true
    columns:
      - name: location_id
        constraints:
          - type: foreign_key
            name: fk_order_to_location
            to: ref('locations')
            to_columns: [location_id]
```

### Relationship types

To control cardinality per constraint, add a `relationship_types` dict to the model's `meta`, keyed by constraint name — mirroring how `relationship_labels` works:

```yaml
models:
  - name: orders
    meta:
      relationship_types:
        fk_order_to_location: many-to-one
        fk_order_to_customer: zero-to-many
    config:
      contract:
        enforced: true
    constraints:
      - type: foreign_key
        name: fk_order_to_location
        to: ref('locations')
        columns: [location_id]
        to_columns: [location_id]
      - type: foreign_key
        name: fk_order_to_customer
        to: ref('customers')
        columns: [customer_id]
        to_columns: [customer_id]
```

Supported values: `zero-to-many`, `zero-to-one`, `one-to-one`, `many-to-many`, `one-to-many`, `many-to-one` (default).

## New module(s)?

If you've got an idea of having new type of module(s) to parse ERs, feel free to:

- To submit yours [here](https://github.com/datnguye/dbterd/issues/new/?title=[FEAT]-What-is-your-idea)
- Or to check [Contribution](./development/contributing-guide.html) for pulling a request!
