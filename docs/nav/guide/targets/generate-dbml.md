# Generate DBML

## 1. Produce your manifest json

In your dbt project (I am using dbt-resto/[integration_tests](https://github.com/datnguye/dbt-resto) for demo purpose), try to build the docs:

```bash
dbt docs generate
```

## 2. Generate DBML

Copy `manifest.json` and `catalog.json` into a specific folder OR do nothing and let's assume we're using `dbt/target` directory, and run

```bash
dbterd run -ad "/path/to/dbt/target" -o "/path/to/output"
# dbterd run -ad "samples/dbtresto" -s model.dbt_resto -ns model.dbt_resto.staging
```

File `./target/output.dbml` will be generated as the result

## 3. Build database docs site (Optional)

Assuming you're already familiar with [dbdocs](https://dbdocs.io/docs#installation)

```bash
dbdocs build "/path/to/output/output.dbml"
# dbdocs build "./target/output.dbml"
```

Your terminal should provide the info as below:

```bash
√ Parsing file content
? Project name:  poc
‼ Password is not set for 'poc'
√ Done. Visit: https://dbdocs.io/datnguye/poc
```

The site will be looks like:

![screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png)

Result after applied Model Selection:
![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)
