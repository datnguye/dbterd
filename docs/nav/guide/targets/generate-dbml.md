# Generate DBML

## 1. Produce your manifest json

In your dbt project (I am using dbt-resto/[integration_tests](https://github.com/datnguye/dbt-resto) for demo purpose), try to build the docs:

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbt docs generate</span>
    <span data-ty>01:40:58  Running with dbt=1.3.4</span>
    <span data-ty>01:40:58  Partial parse save file not found. Starting full parse.</span>
    <span data-ty>01:41:00  Found 0 models, 0 tests, 0 snapshots, 0 analyses, 356 macros, 1 operation, 0 seed files, 0 sources, 0 exposures, 0 metrics</span>
    <span data-ty>01:41:00  </span>
    <span data-ty>01:41:00  Concurrency: 4 threads (target='postgres')</span>
    <span data-ty>01:41:00  </span>
    <span data-ty>01:41:00  Done.</span>
    <span data-ty>01:41:00  Building catalog</span>
    <span data-ty>01:41:00  Catalog written to .\target\catalog.json</span>
</div>

<!-- In-article Ad -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9818368894527523"
     crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block; text-align:center;"
     data-ad-layout="in-article"
     data-ad-format="fluid"
     data-ad-client="ca-pub-9818368894527523"
     data-ad-slot="5802605910"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>

## 2. Generate DBML

Copy `manifest.json` and `catalog.json` into a specific folder OR do nothing and let's assume we're using `dbt/target` directory, and run

!!! tip "Sample Usage"
    `dbterd run -ad "/path/to/dbt/target" -o "/path/to/output"`

<div class="termynal" data-ty-startDelay="1200">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd run -ad "samples/dbtresto" -s model.dbt_resto</span>
    <span data-ty>2023-05-06 08:17:54,413 - dbterd - INFO - Run with dbterd==?.?.? (main.py:54)</span>
    <span data-ty>2023-05-06 08:17:54,715 - dbterd - INFO - target/output.dbml (executor.py:75)</span>
</div>

File `./target/output.dbml` will be generated as the result

## 3. Build database docs site (Optional)

Assuming you're already familiar with [dbdocs](https://dbdocs.io/docs#installation)

!!! tip "Sample Usage"
    `dbdocs build "/path/to/output/output.dbml"`

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbdocs build "./target/output.dbml"</span>
    <span data-ty>√ Parsing file content</span>
    <span data-ty>? Project name:  poc</span>
    <span data-ty>‼ Password is not set for 'poc'</span>
    <span data-ty>√ Done. Visit: https://dbdocs.io/datnguye/poc</span>
</div>

The site will be looks like:

![screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png](./../../../assets/images/screencapture-dbdocs-io-datnguye-poc-2022-12-18-22_02_28.png)

Result after applied Model Selection:
![screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png](./../../../assets/images/screencapture-dbdocs-io-datnguye-poc-2023-02-25-10_29_32.png)
