# CLI Reference (dbterd)

Run `dbterd --help` or `dbterd -h` to see the basic guideline for CLI Reference

<div class="termynal" data-termynal data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd -h</span>
    <span data-ty>Usage: dbterd [OPTIONS] COMMAND [ARGS]...<br />
<br />
Tools for producing diagram-as-code<br />
<br />
Options:<br />
--version   Show the version and exit.<br />
-h, --help  Show this message and exit.<br />
<br />
Commands:<br />
debug  Inspect the hidden magics<br />
run    Run the convert<br />
    </span>
</div>

## dbterd run

Command to generate diagram-as-a-code file

**Examples:**
=== "CLI (within dbt project)"

    ```bash
    dbt docs generate
    dbterd run [-t dbml or -t mermaid]
    ```

=== "--help (-h)"
    ```
    Usage: dbterd run [OPTIONS]

    Run the convert

    Options:
        -ad, --artifacts-dir TEXT     Specified the full path to dbt artifacts path
                                        which known as /target directory  [default:
                                        C:\Users\DAT\Documents\Sources\dbterd\target]
        -o, --output TEXT             Output the result file. Default to the same
                                        target dir  [default:
                                        C:\Users\DAT\Documents\Sources\dbterd\target]
        -s, --select TEXT             Selecttion criteria
        -ns, --exclude TEXT           Exclusion criteria
        -t, --target TEXT             Target to the diagram-as-code platform
                                        [default: dbml]
        -a, --algo TEXT               Specified algorithm in the way to detect
                                        diagram connectors  [default:
                                        test_relationship]
        -mv, --manifest-version TEXT  Specified dbt manifest.json version
        -cv, --catalog-version TEXT   Specified dbt catalog.json version
        -rt, --resource-type TEXT     Specified dbt resource type(seed, model,
                                        source, snapshot),default:model, use examples,
                                        -rt model -rt source
        --omit-columns                Flag to omit columns in diagram. Currently
                                        only mermaid is supported
        -h, --help                    Show this message and exit.
    ```

### dbterd run --select (-s)

Selection criteria.
> Select all dbt models if not specified, supports mulitple options

Rules:

- By `name`: model name starts with input string
- By `exact`: exact model name, formed as `exact:model.package.name`
- By `schema`: schema name starts with an input string, formed as `schema:<your_schema_name>`
- By `wildcard`: model name matches to a [wildcard pattern](https://docs.python.org/3/library/fnmatch.html), formed as `wildcard:<your_wildcard>`
- By `exposure`: exposure name, exact match

**Examples:**
=== "CLI (by name)"

    ```bash
    dbterd run -s "model.package.partital_name"
    ```
=== "CLI (by exact name)"

    ```bash
    dbterd run -s "exact:model.package.name"
    ```
=== "CLI (by schema)"

    ```bash
    dbterd run -s "schema:my_schema_name"
    ```
=== "CLI (by wildcard)"

    ```bash
    dbterd run -s "wildcard:*xyz"
    ```
=== "CLI (by exposure)"

    ```bash
    dbterd run -s "exposure:my_exposure_name"
    ```

#### `AND` and `OR` logic

- `AND` logic is applied to a single selection splitted by comma (,)
- `OR` logic is applied to 2+ selection

**Examples:**
=== "AND"

    ```bash
    # All models belong to 'abc' schema AND also need to match the pattern of '*xyz.*'
    dbterd run -s schema:abc,wildcard:*xyz.*
    ```
=== "OR"

    ```bash
    # All models belong to 'abc' schema, OR match to the pattern of '*xyz.*'
    dbterd run -s schema:abc -s wildcard:*xyz.*
    ```

### dbterd run --exclude (-ns)

Exclusion criteria. Rules are the same as Selection Criteria.
> Do not exclude any dbt models if not specified, supports mulitple options

**Examples:**
=== "CLI"

    ```bash
    dbterd run -ns 'model.package_name.table'
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --exclude 'model.package_name.table'
    ```

### dbterd run --artifacts-dir (-ad)

Configure the path to directory containing dbt artifact files.

It will take the the nested `/target` directory of `--dbt-project-dir` if not specified.

> Default to the current directory's `/target` if both this option and `--dbt-project-dir` option are not specified

**Examples:**
=== "CLI"

    ```bash
    dbterd run -ad "./target"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --artifacts-dir "./target"
    ```

### dbterd run --output (-o)

Configure the path to directory containing the output diagram file.
> Default to `./target`

**Examples:**
=== "CLI"

    ```bash
    dbterd run -o "./target"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --output "./target"
    ```

### dbterd run --output-file-name (-ofn)

Configure the output file name
> Default to `output.{modulename}` which is defined in the target module

**Examples:**
=== "CLI"

    ```bash
    dbterd run -ofn "erd.dbml"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --output-file-name "erd.dbml"
    ```

### dbterd run --target (-t)

> Default to `dbml`

Supported target, please visit [Generate the Targets](https://dbterd.datnguyen.de/latest/nav/guide/targets/generate-dbml.html)

**Examples:**
=== "CLI"

    ```bash
    dbterd run -t dbml
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --target dbml
    ```

### dbterd run --algo (-a)

Specified algorithm in the way to detect diagram connectors
> Default to `test_relationship`

In the advanced use case, the test name can be configurable by following syntax:

`{algorithm_name}:(name:{contains_test_name}|c_from:{referencing_column_name}|c_to:{referenced_column_name})`

In the above:

- `algorithm_name`: `test_relationship` (only supported value now)
- `contains_test_name`: Configure the test name (detected with `contains` logic). Default to `relationship`
- `c_from`: Configure the test metadata attribute (1) for the foreign key column name(s). If (1)'s value is multiple columns, it will concat them all   with `_and` wording
      > NOTE: It always looking at the `column_name` attribute firstly
- `c_to`: Configure the test metadata attribute (2) for the referenced column name(s). If (2)'s value is multiple columns, it will concat them all with `_and` wording. Default to `field`

!!! tip "For example, if you would use `dbt-constraints` package"
    The [dbt-constraints](https://hub.getdbt.com/snowflake-labs/dbt_constraints/latest/) package is using different name of test which is close to the contraint names, in this case, you would need to customize the input string here:

    ```bash
    dbterd run \
    --algo "test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)"
    ```

**Examples:**
=== "CLI"

    ```bash
    dbterd run -a test_relationship
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --algo test_relationship
    ```
=== "Use `foreign_key` test"

    ```bash
    dbterd run --algo "test_relationship:(name:foreign_key|c_from:fk_column_name|c_to:pk_column_name)"
    ```

### dbterd run --omit-columns

Flag to omit columns in diagram. Currently only mermaid is supported

> Default to `False`

**Examples:**
=== "CLI"

    ```bash
    dbterd run --target mermaid --omit-columns
    ```

### dbterd run --manifest-version (-mv)

Specified dbt manifest.json version
> Auto detect if not specified

**Examples:**
=== "CLI"

    ```bash
    dbterd run --manifest-version 7
    ```
=== "CLI (long style)"

    ```bash
    dbterd run -mv 7
    ```

### dbterd run --catalog-version (-cv)

Specified dbt catalog.json version
> Auto detect if not specified

**Examples:**
=== "CLI"

    ```bash
    dbterd run --catalog-version 7
    ```
=== "CLI (long style)"

    ```bash
    dbterd run -cv 7
    ```

### dbterd run --resource-type (-rt)

Specified dbt resource type(seed, model, source, snapshot).
> Default to `["model"]`, supports mulitple options

**Examples:**
=== "CLI"

    ```bash
    dbterd run -rt model -rt source
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --resource-type model
    ```

### dbterd run --dbt

Flag to indicate the Selecton to follow dbt's one leveraging Programmatic Invocation
> Default to `False`

**Examples:**
=== "CLI (use dbt selection)"

    ```bash
    dbterd run -s +something --dbt
    # select 'something' and the upstream
    ```
=== "CLI (use dbterd selection)"

    ```bash
    dbterd run -s something
    # select starts with 'something'
    ```

### dbterd run --dbt --dbt-auto-artifact

Flag to indicate force running `dbt docs generate` to the targetted project in order to produce the dbt artifact files.

This option have to be enabled together with `--dbt` option, and will override the value of `--artifacts-dir` to be using the `/target` dir of the value of `--dbt-project-dir`.

> Default to `False`

**Examples:**
=== "CLI"

    ```bash
    dbterd run -s +something --dbt --dbt-auto-artifacts
    ```

### dbterd run --dbt-project-dir (-dpd)

Specified dbt project directory path

You should specified this option if your CWD is not the dbt project dir, and normally used with `--dbt` enabled. It will take the value of `--artifacts-dir` if not specified.

> Default to the current directory if both this option and `--artifacts-dir` option are not specified

**Examples:**
=== "CLI"

    ```bash
    dbterd run -s +something --dbt-project-dir /path/to/dbt/project --dbt
    # select 'something' and the upstream of the dbt project located at /path/to/dbt/project
    # the artifacts dir will probably be assumed as: /path/to/dbt/project/target
    ```

### dbterd run --dbt-target (-dt)

Specified dbt target name

Probably used with `--dbt` enabled.

> Default to the dbt's profile configuration

**Examples:**
=== "CLI"

    ```bash
    dbterd run -s +something --dbt-project-dir /path/to/dbt/project --dbt --dbt-target prod
    # select 'something' and the upstream of the dbt project located at /path/to/dbt/project using target name 'prod'
    # the artifacts dir will probably be assumed as: /path/to/dbt/project/target
    ```

### dbterd run --entity-name-format (-enf)

Decide how the table name is generated on the ERD.

By default, the table name is the dbt node name (`resource_type.package_name.model_name`).

Currently, it supports the following keys in the format:

- `resource.package.model` (by default)
- `database.schema.table`
- Or any other partial forms e.g. `schema.table`, `resource.model`

**Examples:**
=== "CLI"

    ```bash
    dbterd run --entity-name-format resource.package.model # by default
    dbterd run --entity-name-format database.schema.table # with fqn of the physical tables
    dbterd run --entity-name-format schema.table # with schema.table only
    dbterd run --entity-name-format table # with table name only
    ```

### dbterd run --dbt-cloud

Decide to download artifact files from dbt Cloud Job Run instead of compiling locally.

Check [Download artifacts from a Job Run](./dbt-cloud/download-artifact-from-a-job-run.md) for more details.

**Examples:**
=== "CLI"

    ```bash
    dbterd run --dbt-cloud
    dbterd run --dbt-cloud --select wildcard:*transaction*
    ```

## dbterd run-metadata

Command to generate diagram-as-a-code file by connecting to dbt Cloud Discovery API using GraphQL connection.

Check [this guideline](./dbt-cloud/read-artifact-from-an-environment.md) for more details.

**Examples:**
=== "CLI"

    ```bash
    dbterd run-metadata [-t dbml or -t mermaid]
    ```

## dbterd debug

Shows hidden configured values, which will help us to see what configs are passed into and how they are evaluated to be used.

**Examples:**
=== "Output"

    ```
    2023-09-08 16:43:45,066 - dbterd - INFO - Run with dbterd==1.0.0 (main.py:54)
    2023-09-08 16:43:45,071 - dbterd - INFO - **Arguments used** (main.py:63)
    2023-09-08 16:43:45,073 - dbterd - DEBUG - {
        "artifacts_dir": "",
        "output": "C:\\Users\\DAT\\Documents\\Sources\\dbterd\\target",
        "select": [],
        "exclude": [],
        "target": "dbml",
        "algo": "test_relationship",
        "manifest_version": null,
        "catalog_version": null,
        "resource_type": [
            "model"
        ],
        "dbt": false,
        "dbt_project_dir": "",
        "dbt_target": null
    } (main.py:64)
    2023-09-08 16:43:45,079 - dbterd - INFO - **Arguments evaluated** (main.py:65)
    2023-09-08 16:43:45,081 - dbterd - INFO - Using dbt artifact dir at: C:\Users\DAT\Documents\Sources\dbterd\target (base.py:41)
    2023-09-08 16:43:45,082 - dbterd - INFO - Using dbt project  dir at: C:\Users\DAT\Documents\Sources\dbterd (base.py:42)
    2023-09-08 16:43:45,084 - dbterd - DEBUG - {
        "artifacts_dir": "C:\\Users\\DAT\\Documents\\Sources\\dbterd\\target",
        "output": "C:\\Users\\DAT\\Documents\\Sources\\dbterd\\target",
        "select": [],
        "exclude": [],
        "target": "dbml",
        "algo": "test_relationship",
        "manifest_version": null,
        "catalog_version": null,
        "resource_type": [
            "model"
        ],
        "dbt": false,
        "dbt_project_dir": "C:\\Users\\DAT\\Documents\\Sources\\dbterd",
        "dbt_target": null
    } (main.py:66)
    ```
