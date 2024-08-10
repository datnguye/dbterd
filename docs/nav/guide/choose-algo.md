# Choosing the algorithm (parsers) to parse the Entity Relationships (ERs)

There are 2 approaches (or 2 modules) we can use here to let `dbterd` look at how the ERs can be recognized between the dbt models:

1. **Test Relationship** ([docs](https://docs.getdbt.com/reference/resource-properties/data-tests#relationships), [source](https://github.com/datnguye/dbterd/blob/main/dbterd/adapters/algos/test_relationship.py)) (default)
2. **Semantic Entities** ([docs](https://docs.getdbt.com/docs/build/entities), [source](https://github.com/datnguye/dbterd/blob/main/dbterd/adapters/algos/semantic.py))

## Test Relationship

During the dbt development, the engineers are supposed to add the consistency checking using `relationships` test function, or similarly specifying the dbt contraints (they're also the tests behind the scenes), given the below example project with [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop).

Let's install the repo:

```shell
git clone https://github.com/dbt-labs/jaffle-shop
cd jaffle-shop
```

Setup the environment, and install the deps including `dbterd`:

```shell
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
pip install dbterd --upgrade
```

In the `order_items.sql` model, we can see 1 sample test:

```yml
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

NO, not yet (maybe!), sometime this module is not going to work perfectly due to:

- Some relationship tests are added from `mart` to `staging` just for ensuring no missing data when moving from a layer to another.
    - That's why we have the [ignore_in_erd](https://dbterd.datnguyen.de/1.15/nav/metadata/ignore_in_erd.html) metadata config.
- We have the tests done in separate tools already (e.g. Soda), there is no reason to duplicate the (relationship) tests here.
    - No problem! Let's still add it with `where: 1=0` or with the dummy relationship tests (see this [blogpost](https://medium.com/@vaibhavchopda04/generating-erds-from-dbt-projects-a-code-driven-approach-83abb957f483))

In case that we don't want to leverage the dbt tests still, let's move on the next section for the alternative 🏃

## Semantic Entities

Since dbt v1.6, dbt has supported the Semantic Layer (SL) with Metric Flow ([docs](https://docs.getdbt.com/docs/build/about-metricflow)), we have the ability to define entities in our semantic modelling, telling `metricflow` how to join tables together. Therefore, it now becomes the 2nd parser for our choice of usage if we have implemented the dbt SL already.

`dbterd` can now look for the Semantic [Entities](https://docs.getdbt.com/docs/build/entities) (`primary` and `foreign`) in order to understand the ERs, subsequently produce the ERD code.

Let's use the above [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop) project again, here is the sample code which was implemented in the repo for the semantic models: `order_item` and `orders`:

```yml
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

```shell
dbterd run -enf table -a semantic
```

The result DBML code will be the same as the 1st option. Voila! 🎉🎉

## New module(s)?

If you've got an idea of having new type of module(s) to parse ERs, feel free to:

- To submit yours [here](https://github.com/datnguye/dbterd/issues/new/?title=[FEAT]-What-is-your-idea)
- Or to check [Contribution](./development/contributing-guide.html) for pulling a request!
