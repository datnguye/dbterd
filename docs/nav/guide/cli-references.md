# CLI Reference (dbterd)

Run `--help` or `-h` to see the basic guideline for CLI Reference

Shows the main commands

```
Usage: dbterd [OPTIONS] COMMAND [ARGS]...

  Tools for producing diagram-as-code

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  debug  Inspect the hidden magics
  run    Run the convert
```


## run
::: dbterd.run

Generate diagram-as-a-code file. Supports: [DBML](https://www.dbml.org/home/)

**Examples:**
=== "CLI (within dbt project)"

    ```bash
    dbt docs generate
    dbterd run
    ```

=== "--help (-h)"
    ```
    Usage: dbterd run [OPTIONS]

    Run the convert

    Options:
    -ad, --artifacts-dir TEXT     Specified the full path to dbt artifacts path
                                    which known as /target directory  [default:
                                    C:\Users\DAT\Documents\Sources\dbterd\target]
    -mp, --manifest-path TEXT     __DEPRECATED_WARNING__: Specified the full
                                    directory path to dbt manifest.json file. Use
                                    --artifacts-dir instead.
    -o, --output TEXT             Output the result file. Default to the same
                                    target dir  [default:
                                    C:\Users\DAT\Documents\Sources\dbterd\target]
    -s, --select TEXT             Selecttion criteria. Support 'starts with' a
                                    string
    -ns, --exclude TEXT           Exclusion criteria. Support 'not starts with'
                                    a string
    -t, --target TEXT             Target to the diagram-as-code platform
                                    [default: dbml]
    -a, --algo TEXT               Specified algorithm in the way to detect
                                    diagram connectors  [default:
                                    test_relationship]
    -mv, --manifest-version TEXT  Specified dbt manifest.json version
    -rt, --resource-type TEXT     Specified dbt resource type(seed, model,
                                    source, snapshot),default:model, use examples,
                                    -rt model -rt source
    -h, --help                    Show this message and exit.
    ```

### --artifacts-dir (-ad)
::: dbterd.run.--artifacts-dir

Configure the path to directory containing dbt artifact files.
> Default to `./target`

**Examples:**
=== "CLI"

    ```bash
    dbterd run -ad "./target"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --artifacts-dir "./target"
    ```

**Examples:**
=== "CLI"

    ```bash
    dbterd run -mp "./target"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --manifest-path "./target"
    ```

### --output (-o)
::: dbterd.run.--output

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

### --select (-s)
::: dbterd.run.--select

Selecttion criteria. Support 'starts with' a string where string is:
  - table name (or part of it)
  - schema name (or part of it) formed as `schema:<your_schema_name>
> Select all dbt models if not specified

**Examples:**
=== "CLI (by table)"

    ```bash
    dbterd run -s "model.package_name.model_name"
    ```
=== "CLI (by schema)"

    ```bash
    dbterd run -s "schema:my_schema_name"
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --select "<your-criteria>"
    ```

### --exclude (-ns)
::: dbterd.run.todo

Configure todo
> Default to `todo`

**Examples:**
=== "CLI"

    ```bash
    dbterd run todo
    ```
=== "CLI (long style)"

    ```bash
    dbterd run todo
    ```

### --target (-t)
::: dbterd.run.--target

Target to the diagram-as-code platform
> Default to `dbml`, currently only supported option

**Examples:**
=== "CLI"

    ```bash
    dbterd run -t dbml
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --target dbml
    ```

### --algo (-a)
::: dbterd.run.--algo

Specified algorithm in the way to detect diagram connectors
> Default to `test_relationship`, currently only supported option

**Examples:**
=== "CLI"

    ```bash
    dbterd run -a test_relationship
    ```
=== "CLI (long style)"

    ```bash
    dbterd run --algo test_relationship
    ```

### --manifest-version (-mv)
::: dbterd.run.--manifest-version

Specified dbt manifest.json version
> Default to `todo`

**Examples:**
=== "CLI"

    ```bash
    dbterd run todo
    ```
=== "CLI (long style)"

    ```bash
    dbterd run todo
    ```

### --resource-type (-rt)
::: dbterd.run.--resource-type

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

### ⚠ DEPRECATED WARNING

#### --manifest-path (-mp) (DEPRECATED soon)
::: dbterd.run.DEPRECATED.--manifest-path

Configure the path to directory containing dbt `manifest.json` file.
> Default to `./target`


## debug
::: dbterd.debug

Shows hidden configured values

**Examples:**
=== "Output"

    ```
    2023-04-08 10:15:03,611 - dbterd - INFO - Run with dbterd==0.2.0 (main.py:43)
    2023-04-08 10:15:03,612 - dbterd - INFO - **Arguments used** (main.py:52)
    2023-04-08 10:15:03,613 - dbterd - DEBUG - {
        "artifacts_dir": "C:\\Users\\DAT\\Documents\\Sources\\dbterd\\target",
        "manifest_path": null,
        "output": "C:\\Users\\DAT\\Documents\\Sources\\dbterd\\target",
        "select": null,
        "exclude": null,
        "target": "dbml",
        "algo": "test_relationship",
        "manifest_version": null,
        "resource_type": [
            "model"
        ]
    } (main.py:53)
    2023-04-08 10:15:03,614 - dbterd - INFO - **Context used** (main.py:54)
    2023-04-08 10:15:03,614 - dbterd - DEBUG - {} (main.py:55)
    ```
