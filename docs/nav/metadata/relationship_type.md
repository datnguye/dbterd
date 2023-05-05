## Decide to enforce Relationship Type

Add `relationship_type` attribute into your test's meta:

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
                relationship_type: many-to-one
```

Default value: `many-to-one` if the meta config is not specified

List of accepted values:

| Relationship Type | Programatic Symbol |
|--------|--------|
| one-to-many | 1n |
| zero-to-many | 0n |
| many-to-many | nn |
| one-to-one | 11 |
| many-to-one | n1 |
| Not specified/Invalid value | n1 |

> NOTE: Known as we could configure multiple relationship types but in the best practice we should always have `many-to-one`
