# Generate Markdown with Mermaid ERD inclusive

## 1. Generate mermaid ERD content

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd run -t mermaid -ad "samples/dbtresto" -s schema:dbt.mart</span>
    <span data-ty>2023-05-06 08:17:54,413 - dbterd - INFO - Run with dbterd==?.?.? (main.py:54)</span>
    <span data-ty>2023-05-06 08:17:54,715 - dbterd - INFO - target/output.md (executor.py:75)</span>
</div>

## 2. Copy mermaid to ERD.md

!!! tip "Linux/MacOs"
    We'll use `echo` and `cat` to copy content over into the target Markdown file.

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">echo \`\`\`mermaid          >  ./samples/dbtresto/ERD.md</span>
    <span data-ty="input" data-ty-prompt="$ ~/repo>">echo ---                    >> ./samples/dbtresto/ERD.md</span>
    <span data-ty="input" data-ty-prompt="$ ~/repo>">echo title: Sample ERD      >> ./samples/dbtresto/ERD.md</span>
    <span data-ty="input" data-ty-prompt="$ ~/repo>">echo ---                    >> ./samples/dbtresto/ERD.md</span>
    <span data-ty="input" data-ty-prompt="$ ~/repo>">cat ./target/output.md      >> ./samples/dbtresto/ERD.md</span>
    <span data-ty="input" data-ty-prompt="$ ~/repo>">echo \`\`\`                 >> ./samples/dbtresto/ERD.md</span>
    <span data-ty data-ty-prompt="$ ~/repo>"></span>
</div>

### 3. Commit it and check it on GitHub

Check out the [sample](https://github.com/datnguye/dbterd/blob/main/samples/dbtresto/ERD.md) output:

![erd](./../../../assets/images/sample-mermaid-ERD.png)
