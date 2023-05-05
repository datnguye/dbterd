# Generate GraphViz ERD

## 1. Install GraphViz CLI

```bash
sudo apt install graphviz
```

> Check [installations](https://graphviz.org/download/#linux) for more details

## 2. Generate GraphViz ERD content

```bash
dbterd run -t graphviz -ad "samples/dbtresto" -o "target" -s schema:dbt.mart
# Expected: ./target/output.graphviz
```

## 2. Export to PNG

```bash
dot -Tpng ./target/output.d2 > ./target/output.png
```

### 3. Embeded into Markdown

```markdown
# Sample GraphViz ERD

![graphviz](./target/output.png)
```

Sample Output:

![graphviz](https://github.com/datnguye/dbterd/blob/main/samples/dbtresto/graphviz.png)
