from dbterd.adapters.targets.dbml.engine import engine


def run(manifest, catalog, **kwargs):
    return ("output.dbml", engine.parse(manifest, catalog, **kwargs))
