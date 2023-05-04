## Decide to exclude Relationship Tests from ERD generated

Add `ignore_in_erd` attribute into your test's meta:
```yml
version: 2

models:
  - name: your_model
    columns:
      - name: your_column
        tests:
          - relationships_test:
              to: ref('your_other_model')
              field: your_other_column
              meta:
                ignore_in_erd: 1
```

Default value: `0` if the meta config is not specified
