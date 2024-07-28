# dbterd

Generate the ERD-as-a-code ([DBML](https://dbdiagram.io/d), [Mermaid](https://mermaid-js.github.io/mermaid-live-editor/), [PlantUML](https://plantuml.com/ie-diagram), [GraphViz](https://graphviz.org/), [D2](https://d2lang.com/)) from dbt artifact files (`dbt Core`) or from dbt metadata (`dbt Cloud`)

Entity Relationships are configurably detected by ([docs](https://dbterd.datnguyen.de/latest/nav/guide/cli-references.html#dbterd-run-algo-a)):

- [Test Relationships](https://docs.getdbt.com/reference/resource-properties/data-tests#relationships) (default)
- [Semantic Entities](https://docs.getdbt.com/docs/build/entities) (use `-a` option)

[![PyPI version](https://badge.fury.io/py/dbterd.svg)](https://pypi.org/project/dbterd/)
![python-cli](https://img.shields.io/badge/CLI-Python-FFCE3E?labelColor=14354C&logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.9|3.10|3.11|3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![codecov](https://codecov.io/gh/datnguye/dbterd/branch/main/graph/badge.svg?token=N7DMQBLH4P)](https://codecov.io/gh/datnguye/dbterd)

```bash
pip install dbterd --upgrade
```

Verify installation:

```bash
dbterd --version
```

> [!TIP]
> For `dbt-core` Users, it's highly recommended to upgrade `dbt-artifacts-parser` to the latest version in order to support the newer `dbt-core` version which would cause to have the [new manifest / catalog json schema](https://schemas.getdbt.com/):</br>
> 👉 `pip install dbt-artifacts-parser --upgrade`

## Quick examine with existing samples

- Play with CLIs:

  <details>
    <summary>Click me</summary>

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

    # your own sample without committing to repo
    dbterd run -ad samples/local -rt model -rt source
    ```

  </details>

- Play with Python API (whole ERD):

    ```python
    from dbterd.api import DbtErd

    erd = DbtErd().get_erd()
    print("erd (dbml):", erd)

    erd = DbtErd(target="mermaid").get_erd()
    print("erd (mermaid):", erd)
    ```

- Play with Python API (1 model's ERD):

    ```python
    from dbterd.api import DbtErd

    dim_prize_erd = DbtErd(target="mermaid").get_model_erd(
        node_unique_id="model.dbt_resto.dim_prize"
    )
    print("erd of dim_prize (mermaid):", dim_prize_erd)
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

🏃Check out the [Quick Demo](https://dbterd.datnguyen.de/latest/nav/guide/targets/generate-dbml.html) with DBML!

## Contributing ✨

If you've ever wanted to contribute to this tool, and a great cause, now is your chance!

See the contributing docs [CONTRIBUTING](https://dbterd.datnguyen.de/latest/nav/development/contributing-guide.html) for more information.

If you've found this tool to be very helpful, please consider giving the repository a star, sharing it on social media, or even writing a blog post about it 💌

[![dbterd stars](https://img.shields.io/github/stars/datnguye/dbterd.svg?logo=github&style=for-the-badge&label=Star%20this%20repo)](https://github.com/datnguye/dbterd)
[![buy me a coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?logo=buy-me-a-coffee&logoColor=white&labelColor=ff813f&style=for-the-badge)](https://www.buymeacoffee.com/datnguye)

Finally, super thanks to our *Contributors*:

<a href="https://github.com/datnguye/dbterd/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datnguye/dbterd" />
</a>

</br>
