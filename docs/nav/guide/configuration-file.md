# Configuration Files

`dbterd` supports configuration files to streamline your workflow and reduce the need for repetitive CLI arguments. Think of it as your ERD generation control center – set it once, use it everywhere!

## Supported Configuration Files

`dbterd` automatically discovers configuration files in your current directory:

1. **`.dbterd.yml`** - YAML configuration file (recommended for most users)
2. **`pyproject.toml`** - TOML configuration with `[tool.dbterd]` section (great for Python projects)

!!! tip "Priority Order"
    If both files exist, `dbterd` checks them in this order:

    1. `pyproject.toml` (if it contains `[tool.dbterd]` section)
    2. `.dbterd.yml`

    CLI arguments always override configuration file values.

## Quick Start

### Initialize Configuration

The easiest way to get started is using the `dbterd init` command:

<div class="termynal" data-termynal data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">dbterd init</span>
    <span data-ty>Created configuration file: .dbterd.yml | Template type: dbt-core</span>
    <a href="#" data-terminal-control="">restart ↻</a>
</div>

This creates a `.dbterd.yml` file with all available options documented and ready to customize.

**Available templates:**

=== "dbt Core (default)"

    ```bash
    `dbterd` init [--template dbt-core]
    ```

    Creates configuration for local dbt projects using artifact files.

=== "dbt Cloud"

    ```bash
    `dbterd` init --template dbt-cloud
    ```

    Creates configuration for dbt Cloud with API connection settings.

!!! note "Overwrite existing config"
    Use `--force` to overwrite an existing configuration file:
    ```bash
    `dbterd` init --force
    ```

## Configuration File Examples

### YAML Configuration (`.dbterd.yml`)

Here's a practical example for a dbt Core project:

```yaml
# Output Settings
target: mermaid
output: ./docs/erd
output-file-name: schema.mmd

# Selection & Filtering
select:
  - fct_*
  - dim_*
exclude:
  - stg_*

# Resource Types
resource-type:
  - model
  - source

# Relationship Detection
algo: test_relationship

# Entity Naming
entity-name-format: schema.table
omit-entity-name-quotes: false
omit-columns: false

# dbt Artifact Settings
artifacts-dir: ./target
bypass-validation: true

# dbt Project Settings (if using --dbt flag)
dbt: false
dbt-project-dir: .
dbt-auto-artifacts: false
```

### TOML Configuration (`pyproject.toml`)

Add `dbterd` configuration to your existing `pyproject.toml`:

```toml
[tool.dbterd]
target = "mermaid"
output = "./docs/erd"
output-file-name = "schema.mmd"

select = [
    "fct_*",
    "dim_*"
]
exclude = ["stg_*"]

resource-type = ["model", "source"]
algo = "test_relationship"

entity-name-format = "schema.table"
omit-entity-name-quotes = false
omit-columns = false

artifacts-dir = "./target"
bypass-validation = true

dbt = false
dbt-project-dir = "."
dbt-auto-artifacts = false
```

### dbt Cloud Configuration

For projects using dbt Cloud:

=== "YAML"

    ```yaml
    # Output Settings
    target: dbml
    output: ./target

    # dbt Cloud Settings
    dbt-cloud: true

    # Nested dbt-cloud configuration
    dbt-cloud:
      host-url: cloud.getdbt.com
      account-id: "12345"
      job-id: "67890"
      # Note: Store service-token in environment variable DBTERD_DBT_CLOUD_SERVICE_TOKEN
      api-version: v2

    # Selection
    select:
      - wildcard:*transaction*

    # Resource Types
    resource-type:
      - model
    ```

=== "TOML"

    ```toml
    [tool.dbterd]
    target = "dbml"
    output = "./target"
    dbt-cloud = true

    [tool.dbterd.dbt-cloud]
    host-url = "cloud.getdbt.com"
    account-id = "12345"
    job-id = "67890"
    # Note: Store service-token in environment variable DBTERD_DBT_CLOUD_SERVICE_TOKEN
    api-version = "v2"

    [[tool.dbterd.select]]
    "wildcard:*transaction*"

    [[tool.dbterd.resource-type]]
    "model"
    ```

!!! warning "Security Best Practice"
    Never store sensitive values like `service-token` in configuration files. Use environment variables instead:
    ```bash
    export DBTERD_DBT_CLOUD_SERVICE_TOKEN="your_token_here"
    ```

## Available Configuration Options

All CLI parameters can be configured in files. Here's the complete reference:

### Output Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `target` | string | `dbml` | Output format (dbml, mermaid, plantuml, graphviz, d2, drawdb) |
| `output` | string | `./target` | Output directory path |
| `output-file-name` | string | - | Custom output file name |

### Selection & Filtering

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `select` | list | `[]` | Model/resource selection criteria |
| `exclude` | list | `[]` | Model/resource exclusion criteria |
| `resource-type` | list | `["model"]` | Resource types to include (model, source, seed, snapshot) |

### Relationship Detection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `algo` | string | `test_relationship` | Algorithm for detecting relationships |

### Entity Naming

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity-name-format` | string | `resource.package.model` | Format for entity names |
| `omit-entity-name-quotes` | boolean | `false` | Remove quotes from entity names (dbml only) |
| `omit-columns` | boolean | `false` | Hide columns in diagram (mermaid only) |

### Artifact Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `artifacts-dir` | string | `./target` | Path to dbt artifacts directory |
| `manifest-version` | string | auto-detect | dbt manifest.json version |
| `catalog-version` | string | auto-detect | dbt catalog.json version |
| `bypass-validation` | boolean | `true` | Bypass Pydantic validation errors |

### dbt Project Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dbt` | boolean | `false` | Use dbt's selection syntax |
| `dbt-project-dir` | string | `.` | Path to dbt project directory |
| `dbt-target` | string | - | dbt target name |
| `dbt-auto-artifacts` | boolean | `false` | Auto-generate artifacts via programmatic invocation |

### dbt Cloud Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dbt-cloud` | boolean | `false` | Enable dbt Cloud API integration |
| `dbt-cloud.host-url` | string | `cloud.getdbt.com` | dbt Cloud host URL |
| `dbt-cloud.account-id` | string | - | dbt Cloud account ID |
| `dbt-cloud.run-id` | string | - | dbt Cloud run ID |
| `dbt-cloud.job-id` | string | - | dbt Cloud job ID |
| `dbt-cloud.service-token` | string | - | dbt Cloud service token (use env var!) |
| `dbt-cloud.api-version` | string | `v2` | dbt Cloud API version |
| `dbt-cloud.environment-id` | string | - | Environment ID (for run-metadata) |
| `dbt-cloud.query-file-path` | string | - | Custom GraphQL query file path |

!!! info "Environment Variables"
    All options support environment variable overrides with the `DBTERD_*` prefix. For example:
    ```bash
    export DBTERD_TARGET=mermaid
    export DBTERD_OUTPUT=./my-docs
    ```

## Usage Patterns

### Override Config with CLI Arguments

Configuration files provide defaults, but CLI arguments always take precedence:

```bash
# Config says target: dbml
# CLI overrides to mermaid
`dbterd` run --target mermaid
```

### Multiple Environments

Use different config files for different environments:

=== "Development"

    ```bash
    # .dbterd.dev.yml
    target: mermaid
    artifacts-dir: ./target
    select:
      - "*"
    ```

    ```bash
    # Use explicitly
    `dbterd` run  # Uses default config if exists
    ```

=== "Production"

    ```bash
    # .dbterd.prod.yml
    target: dbml
    artifacts-dir: ./target
    select:
      - fct_*
      - dim_*
    exclude:
      - stg_*
    ```

!!! note "Custom config file paths"
    Currently, `dbterd` only auto-discovers config files in the current directory. Support for custom config file paths via `--config` flag is planned for a future release.

### CI/CD Integration

Configuration files work great in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Generate ERD
  run: |
    dbterd run
  env:
    DBTERD_DBT_CLOUD_SERVICE_TOKEN: ${{ secrets.DBT_CLOUD_TOKEN }}
```

The config file provides stable defaults while sensitive values come from secrets.

## Auto-Detection Features

### Artifact Version Detection

`dbterd` now automatically detects manifest and catalog versions from the `metadata.dbt_schema_version` field:

```yaml
# No need to specify versions manually!
artifacts-dir: ./target
# manifest-version: 12  # Auto-detected
# catalog-version: 1    # Auto-detected
```

This means you rarely need to specify `--manifest-version` or `--catalog-version` anymore – `dbterd` figures it out for you!

### Graceful Fallback

If no configuration file exists, `dbterd` falls back to CLI defaults gracefully. This means:

- Existing CLI workflows continue to work unchanged
- You can adopt config files incrementally
- No breaking changes to existing scripts

## Key Naming Convention

Configuration files use **kebab-case** for keys (e.g., `artifacts-dir`, `dbt-cloud`), which automatically converts to the snake_case used internally by Python.

Both styles work in YAML/TOML:

=== "Kebab-case (recommended)"

    ```yaml
    artifacts-dir: ./target
    dbt-project-dir: .
    ```

=== "Snake_case (also works)"

    ```yaml
    artifacts_dir: ./target
    dbt_project_dir: .
    ```

## Troubleshooting

### Config File Not Found

If you create a config file but `dbterd` doesn't use it:

1. Ensure the file is in your current working directory
2. For `pyproject.toml`, verify the `[tool.dbterd]` section exists
3. Check file permissions (must be readable)

### Invalid YAML/TOML Syntax

If you see parsing errors:

```
Configuration error: Invalid YAML in .dbterd.yml:
while parsing a block mapping
```

- Validate your YAML syntax using a linter
- Ensure proper indentation (YAML is whitespace-sensitive)
- Check for missing colons or quotes

### Config Not Taking Effect

If your config seems ignored:

1. CLI arguments override config files – check your command
2. Environment variables override config files – check `env | grep DBTERD`
3. Use `dbterd` debug` to see evaluated configuration values

### Python < 3.11 TOML Support

For Python versions below 3.11, install the `tomli` package:

```bash
pip install tomli
```

Otherwise, you'll see:

```
TOML support requires 'tomli' package for Python < 3.11
```

## Best Practices

1. **Use `.dbterd.yml` for project defaults** - Check it into version control so your team shares the same configuration
2. **Store secrets in environment variables** - Never commit tokens or credentials
3. **Override with CLI for one-off changes** - No need to edit the config for quick experiments
4. **Document your configuration** - Use YAML comments to explain why certain options are set
5. **Start with `dbterd init`** - Let `dbterd` generate a well-documented template for you

## Learn More

- [CLI Reference](./cli-references.md) - Complete CLI documentation
- [Choose the Parser](./choose-algo.md) - Understanding relationship detection algorithms
- [dbt Cloud Integration](./dbt-cloud/download-artifact-from-a-job-run.md) - Using `dbterd` with dbt Cloud
