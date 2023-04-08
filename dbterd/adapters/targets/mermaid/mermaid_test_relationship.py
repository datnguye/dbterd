from dbterd.adapters.algos import test_relationship


def run(manifest, catalog, **kwargs):
    return ("output.md", parse(manifest, catalog, kwargs))


def parse(manifest, catalog, **kwargs):
    tables, relationships = test_relationship.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    # Build Mermaid content
    dbml = None
    return dbml
