# Generate PlantUML

## 1. Generate PlantUML ERD content

<div class="termynal" data-ty-startDelay="600">
    <span data-ty="input" data-ty-prompt="$ ~/repo>">dbterd run -t plantuml -ad "samples/dbtresto" -s schema:dbt.mart</span>
    <span data-ty>2023-05-06 08:17:54,413 - dbterd - INFO - Run with dbterd==?.?.? (main.py:54)</span>
    <span data-ty>2023-05-06 08:17:54,715 - dbterd - INFO - target/output.plantuml (executor.py:75)</span>
</div>

## 2. Wrapping UML up to the web server

- Go to [PlantUML Web Server](http://www.plantuml.com/plantuml/uml)
- Paste the PlantUML content generated as above
- Wait for a second and get the URL

### 3. Embed the PlantUML URL into Markdown

```markdown
![](https://www.plantuml.com/plantuml/dpng/{your-hash})
```

![erd](https://www.plantuml.com/plantuml/dpng/fLRRZgCm37tlLw3vW4hbGgLzcZ-9N71tK251IPZPxhR_lh08gnjCZ3HzAPpZayknu_3kF5W_TEq1jM_yFNdhJ8tjiRvuPT5vSwoRJbtChxVapo4PV-EZkk4z-P5yWgq-m1BQr0nOWySHdlu8i-Y6rYizT1UqRcGrgRW8THf36kqts3JAPb4sZx95b2sZx9dOPzJPoPZ5skbvyfRyuZmax1xC_uLu2w3EQF_1OKf3XqosxWXsvy9xs_ocbVzx2Sg2y6KolMQChN7FX5Ue5cUNAUStzGdjW2zRD5KrM8kwua7L6wTEsrIwJMNRLBvD5TjKkKsTNwWMd5VGzmWMT4M545AqEIaWbG8oAI2N0Wefe9G2pXImhohKrLYimFcbF9Rt-V24it6dYXJKbwYKIITtBnhb5AOmtjT8bygwbDDbiYxZTBciopbT8UiAJbUAEWhPctjN6TledvJwaM9w4LSHiKuoZOhgj4BI5PAja7o552larGWB-aQdzzeQ2E2KXpCUpdcuuE6IOD7lEKtaCn34Vn4mA7zHy5UVDifSrPVHPDIYdrD5ooQyXwR-3swScXaFDzHxoyfXUDc8vpwyTuJM_JmamYNtV1oFZqVac-6G24cAZJ3kvri3pAxAGyYxU4TT3rtx5m00)

## Known Limitations💡

- PlantUML connectors don't seem to support indicating the columns which are related to the Relationship
- The question _"How to automate the markdown image URL generation?"_ remains open
