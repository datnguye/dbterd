# Generate markdown with mermaid ERD inclusive

### 1. Generate mermaid ERD content
```
dbterd run -t mermaid -ad "samples/dbtresto" -o "target" -s schema:dbt.mart -ns model.dbt_resto.staging
# Expected: ./target/output.md
```

### 2. Copy mermaid to ERD.md
```bash
echo ```mermaid             >  ./samples/dbtresto/ERD.md
echo ---                    >> ./samples/dbtresto/ERD.md
echo title: Sample ERD      >> ./samples/dbtresto/ERD.md
echo ---                    >> ./samples/dbtresto/ERD.md
cat ./target/output.md      >> ./samples/dbtresto/ERD.md
echo ```                    >> ./samples/dbtresto/ERD.md
```

### 3. Commit it and check it on Github

Check out the [sample](https://raw.githubusercontent.com/datnguye/dbterd/main/ERD.md) output:

![erd](https://raw.githubusercontent.com/datnguye/dbterd/main/assets/images/sample-mermaid-ERD.png)
