# Generate D2 ERD

## 1. Install D2 CLI

```bash
# With --dry-run the install script will print the commands it will use
# to install without actually installing so you know what it's going to do.
curl -fsSL https://d2lang.com/install.sh | sh -s -- --dry-run
# If things look good, install for real.
curl -fsSL https://d2lang.com/install.sh | sh -s --
```

> Check [installations](https://github.com/terrastruct/d2/blob/master/docs/INSTALL.md) for more details

## 2. Generate D2 ERD content

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd run -t d2 -ad "samples/dbtresto" -o "target" -s schema:dbt.mart</span>
    <span data-ty>2023-05-06 08:17:54,413 - dbterd - INFO - Run with dbterd==?.?.? (main.py:54)</span>
    <span data-ty>2023-05-06 08:17:54,715 - dbterd - INFO - target/output.d2 (executor.py:75)</span>
</div>

## 2. Export to SVG

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">d2 -w ./target/output.d2 ./target/output.svg</span>
    <span data-ty data-ty-prompt="$ ~/repo>"></span>
</div>

### 3. Embedded into Markdown

```markdown
# Sample D2 ERD

![d2](./target/output.svg)
```

Sample Output:

![d2](https://raw.githubusercontent.com/datnguye/dbterd/main/samples/dbtresto/d2.svg)
