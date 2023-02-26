# dbterd
CLI to generate DBML file from dbt manifest.json

[![PyPI version](https://badge.fury.io/py/dbterd.svg)](https://badge.fury.io/py/dbterd)
![python-cli](https://img.shields.io/badge/CLI-Python-FFCE3E?labelColor=14354C&logo=python&logoColor=white)

```
pip install dbterd==0.1.1 --upgrade
```

Verify installed version:
```
dbterd --version
```


```bash
dbterd -h
Usage: dbterd [OPTIONS] COMMAND [ARGS]...

  Tools for producing diagram-as-code

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  debug  Inspect the hidden magics
  run    Run the convert

  Specify one of these sub-commands and you can find more help from there.
```

## Quick examine command
```bash
# note that no relationship test = no erd relationship

# select all models in dbt_resto 
dbterd run -mp "./samples/v4-dbtresto" -o "./target"
# select only models in dbt_resto excluding staging
dbterd run -mp "./samples/v4-dbtresto" -o "./target" -s model.dbt_resto -ns model.dbt_resto.staging
# select only models in schema name "mart" excluding staging
dbterd run -mp "./samples/v4-dbtresto" -o "./target" -s schema:mart -ns model.dbt_resto.staging
# select only models in schema full name "dbt.dbo" excluding staging
dbterd run -mp "./samples/v4-dbtresto" -o "./target" -s schema:dbt.mart -ns model.dbt_resto.staging
# other samples
dbterd run -mp "./samples/v7-fivetranlog" -o "./target"
dbterd run -mp "./samples/v7-adfacebook" -o "./target"
```

## Quick DEMO
#### 1. Produce your manifest json

In your dbt project (I am using dbt-resto/[integration_tests](https://github.com/datnguye/dbt-resto) for demo purpose), try to build the docs:
```bash
dbt docs generate
```
    
#### 2. Generate DBML
Copy `manifest.json` into a specific folder, and run 
```
dbterd run -mp "/path/to/manifest" -o "/path/to/output"
# dbterd run -mp "./target/v4-dbtresto" -o "./target" -s model.dbt_resto -ns model.dbt_resto.staging
```

File `./target/output.dbml` will be generated as the result

#### 3. Build database docs site
Assuming you're already familiar with [dbdocs](https://dbdocs.io/docs#installation)
```
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

![screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png](https://github.com/datnguye/dbterd/blob/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png)

Result after applied Model Selection:
![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](https://github.com/datnguye/dbterd/blob/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)

## Decide to exclude Relationship Tests from ERD generated
Add `ignore_in_erd` attribute into your test's meta:
```yml
version: 2

models:
  - name: your_model
    columns:
      - name: your_column
        tests:
          - relationships_test:
              to: ref('your_other_model')
              field: your_other_column
              meta:
                ignore_in_erd: 1
```