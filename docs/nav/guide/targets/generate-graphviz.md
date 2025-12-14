# Generate GraphViz ERD

## 1. Install GraphViz CLI

```bash
sudo apt install graphviz
```

> Check [installations](https://graphviz.org/download/#linux) for more details

## 2. Generate GraphViz ERD content

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd run -t graphviz -ad "samples/dbtresto" -s schema:dbt.mart</span>
    <span data-ty>2023-05-06 08:17:54,413 - dbterd - INFO - Run with dbterd==?.?.? (main.py:54)</span>
    <span data-ty>2023-05-06 08:17:54,715 - dbterd - INFO - target/output.graphviz (executor.py:75)</span>
</div>

## 3. Export to PNG

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dot -Tpng ./target/output.graphviz > ./target/output.png</span>
    <span data-ty data-ty-prompt="$ ~/repo>"></span>
</div>

### 4. Embedded into Markdown

```markdown
# Sample GraphViz ERD

![graphviz](./target/output.png)
```

Sample Output:

![graphviz](https://raw.githubusercontent.com/datnguye/dbterd/main/samples/dbtresto/graphviz.png)
