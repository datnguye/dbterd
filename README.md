# dbterd

CLI to generate Diagram-as-a-code file ([DBML](https://dbdiagram.io/d), [Mermaid](https://mermaid-js.github.io/mermaid-live-editor/), [PlantUML](https://plantuml.com/ie-diagram), [GraphViz](https://graphviz.org/), [D2](https://d2lang.com/)) from dbt artifact files (required: [![dbt](https://img.shields.io/badge/manifest.json-upto--v11-3776AB.svg?style=flat&logo=dbt&logoColor=orange)](https://schemas.getdbt.com/) [![dbt](https://img.shields.io/badge/catalog.json-upto--v1-3776AB.svg?style=flat&logo=dbt&logoColor=orange)](https://schemas.getdbt.com/))

[![PyPI version](https://badge.fury.io/py/dbterd.svg)](https://pypi.org/project/dbterd/)
![python-cli](https://img.shields.io/badge/CLI-Python-FFCE3E?labelColor=14354C&logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.9|3.10|3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![codecov](https://codecov.io/gh/datnguye/dbterd/branch/main/graph/badge.svg?token=N7DMQBLH4P)](https://codecov.io/gh/datnguye/dbterd)

```bash
pip install dbterd --upgrade
```

Verify installation:

```bash
dbterd --version
```

## Quick examine with existing samples

<details>
  <summary>Play with CLI</summary>

  ```bash
  # select all models in dbt_resto
  dbterd run -ad samples/dbtresto
  # select all models in dbt_resto, Select multiple dbt resources
  dbterd run -ad samples/dbtresto -rt model -rt source
  # select only models in dbt_resto excluding staging
  dbterd run -ad samples/dbtresto -s model.dbt_resto -ns model.dbt_resto.staging
  # select only models in schema name mart excluding staging
  dbterd run -ad samples/dbtresto -s schema:mart -ns model.dbt_resto.staging
  # select only models in schema full name dbt.mart excluding staging
  dbterd run -ad samples/dbtresto -s schema:dbt.mart -ns model.dbt_resto.staging

  # other samples
  dbterd run -ad samples/fivetranlog
  dbterd run -ad samples/fivetranlog -rt model -rt source

  dbterd run -ad samples/facebookad
  dbterd run -ad samples/facebookad -rt model -rt source

  dbterd run -ad samples/shopify -s wildcard:*shopify.shopify__*
  dbterd run -ad samples/shopify -rt model -rt source

  dbterd run -ad samples/dbt-constraints -a "test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)"

  # your own sample without commiting to repo
  dbterd run -ad samples/local -rt model -rt source
  ```

</details>

<details>
  <summary>Play with Python API (whole ERD)</summary>

  ```python
  from dbterd.api import DbtErd

  erd = DbtErd().get_erd()
  print("erd (dbml):", erd)

  erd = DbtErd(target="mermaid").get_erd()
  print("erd (mermaid):", erd)
  ```

</details>


<details>
  <summary>Play with Python API (1 model's ERD)</summary>

  ```python
  from dbterd.api import DbtErd

  dim_prize_erd = DbtErd(target="mermaid").get_model_erd(
      node_unique_id="model.dbt_resto.dim_prize"
  )
  print("erd of dim_date (mermaid):", dim_prize_erd)
  ```

  Here is the output:

  ```mermaid
  erDiagram
    "MODEL.DBT_RESTO.DIM_PRIZE" {
      varchar prize_key
      nvarchar prize_name
      int prize_order
    }
    "MODEL.DBT_RESTO.FACT_RESULT" {
      varchar fact_result_key
      varchar box_key
      varchar prize_key
      date date_key
      int no_of_won
      float prize_value
      float prize_paid
      int is_prize_taken
    }
    "MODEL.DBT_RESTO.FACT_RESULT" }|--|| "MODEL.DBT_RESTO.DIM_PRIZE": prize_key
  ```

</details>

## Quick DEMO

Check [Quick Demo](https://dbterd.datnguyen.de/latest/nav/guide/targets/generate-dbml.html) out! And, following is the sample result using `dbdocs`:

![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)

## Contributing ✨

If you've ever wanted to contribute to this tool, and a great cause, now is your chance!

See the contributing docs [CONTRIBUTING](https://dbterd.datnguyen.de/latest/nav/development/contributing-guide.html) for more information.

Finally, super thanks to our *Contributors*:

<a href="https://github.com/datnguye/dbterd/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datnguye/dbterd" />
</a>
