# dbterd
CLI to generate Diagram-as-a-code file ([DBML](https://dbdiagram.io/d), [Mermaid](https://mermaid-js.github.io/mermaid-live-editor/)) from dbt artifact files (required: `manifest.json`, `catalog.json`)

[![PyPI version](https://badge.fury.io/py/dbterd.svg)](https://pypi.org/project/dbterd/)
![python-cli](https://img.shields.io/badge/CLI-Python-FFCE3E?labelColor=14354C&logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.9|3.10|3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![codecov](https://codecov.io/gh/datnguye/dbterd/branch/main/graph/badge.svg?token=N7DMQBLH4P)](https://codecov.io/gh/datnguye/dbterd)

```
pip install dbterd --upgrade
```

Verify installed version:
```
dbterd --version
```

## Quick examine with existing samples
```bash
# select all models in dbt_resto
dbterd run -ad "samples/dbtresto" -o "target"
# select all models in dbt_resto, Select multiple dbt resources
dbterd run -ad "samples/dbtresto" -o "target" -rt "model" -rt "source"
# select only models in dbt_resto excluding staging
dbterd run -ad "samples/dbtresto" -o "target" -s model.dbt_resto -ns model.dbt_resto.staging
# select only models in schema name "mart" excluding staging
dbterd run -ad "samples/dbtresto" -o "target" -s schema:mart -ns model.dbt_resto.staging
# select only models in schema full name "dbt.mart" excluding staging
dbterd run -ad "samples/dbtresto" -o "target" -s schema:dbt.mart -ns model.dbt_resto.staging

# other samples
dbterd run -ad "samples/fivetranlog" -o "target"
dbterd run -ad "samples/fivetranlog" -o "target" -rt "model" -rt "source"

dbterd run -ad "samples/facebookad" -o "target"
dbterd run -ad "samples/facebookad" -o "target" -rt "model" -rt "source"

dbterd run -ad "samples/shopify" -o "target"
dbterd run -ad "samples/shopify" -o "target" -rt "model" -rt "source"

# your own sample without commiting to repo
dbterd run -ad "samples/local" -o "target" -rt "model" -rt "source"
```

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

## Quick DEMO
#### 1. Produce your manifest json

In your dbt project (I am using dbt-resto/[integration_tests](https://github.com/datnguye/dbt-resto) for demo purpose), try to build the docs:
```bash
dbt docs generate
```

#### 2. Generate DBML
Copy `manifest.json` into a specific folder, and run
```
dbterd run -ad "/path/to/dbt/target" -o "/path/to/output"
# dbterd run -ad "samples/dbtresto" -s model.dbt_resto -ns model.dbt_resto.staging
```

File `./target/output.dbml` will be generated as the result

#### 3. Build database docs site (Optional)
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

![screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png)

Result after applied Model Selection:
![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)


## Contributing ✨
If you've ever wanted to contribute to this tool, and a great cause, now is your chance!

See the contributing docs [CONTRIBUTING.md](https://github.com/datnguye/dbterd/blob/main/CONTRIBUTING.md) for more information


## Contributors

Thanks for all the great resources! Can't see your avatar? Check the [contribution guide](https://dbterd.datnguyen.de/latest/nav/development/contributing-guide.html) on how you can submit your resources to the community!

<a href="https://github.com/datnguye/dbterd/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datnguye/dbterd" />
</a>
