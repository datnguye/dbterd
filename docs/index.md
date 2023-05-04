# dbterd

CLI to generate Diagram-as-a-code file ([DBML](https://dbdiagram.io/d), [Mermaid](https://mermaid-js.github.io/mermaid-live-editor/), [PlantUML](https://plantuml.com/ie-diagram)) from dbt artifact files (required: `manifest.json`, `catalog.json`)

[![PyPI version](https://badge.fury.io/py/dbterd.svg)](https://pypi.org/project/dbterd/)
![python-cli](https://img.shields.io/badge/CLI-Python-FFCE3E?labelColor=14354C&logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.9|3.10|3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![codecov](https://codecov.io/gh/datnguye/dbterd/branch/main/graph/badge.svg?token=N7DMQBLH4P)](https://codecov.io/gh/datnguye/dbterd)

<div id="termynal" data-termynal data-termynal class="use-termynal" data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">pip install dbterd --upgrade</span>
    <span data-ty="progress"></span>
    <span data-ty>Successfully installed dbterd</span>
</div>

Verify installed version:

```bash
dbterd --version
```

## Quick examine with existing samples

```bash
# select all models in dbt_resto
dbterd run -ad samples/dbtresto -o target
# select all models in dbt_resto, Select multiple dbt resources
dbterd run -ad samples/dbtresto -o target -rt model -rt source
# select only models in dbt_resto excluding staging
dbterd run -ad samples/dbtresto -o target -s model.dbt_resto -ns model.dbt_resto.staging
# select only models in schema name mart excluding staging
dbterd run -ad samples/dbtresto -o target -s schema:mart -ns model.dbt_resto.staging
# select only models in schema full name dbt.mart excluding staging
dbterd run -ad samples/dbtresto -o target -s schema:dbt.mart -ns model.dbt_resto.staging

# other samples
dbterd run -ad samples/fivetranlog -o target
dbterd run -ad samples/fivetranlog -o target -rt model -rt source

dbterd run -ad samples/facebookad -o target
dbterd run -ad samples/facebookad -o target -rt model -rt source

dbterd run -ad samples/shopify -o target
dbterd run -ad samples/shopify -o target -rt model -rt source

dbterd run -ad samples/dbt-constraints \
    -a "test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)"

# your own sample without commiting to repo
dbterd run -ad samples/local -o target -rt model -rt source
```

## Quick DEMO

Check [Quick Demo](https://dbterd.datnguyen.de/latest/nav/guide/generate-dbml.html) out! And, following is the sample result using `dbdocs`:

![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)


## Contributing ✨

If you've ever wanted to contribute to this tool, and a great cause, now is your chance!

See the contributing docs [CONTRIBUTING](https://dbterd.datnguyen.de/latest/nav/development/contributing-guide.html) for more information.

Finally, super thanks to our *Contributors*:

<a href="https://github.com/datnguye/dbterd/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datnguye/dbterd" />
</a>
