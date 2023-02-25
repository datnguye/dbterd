from dbterd.adapters.targets.dbml.engine import engine


def run(manifest, **kwargs):
    return ("output.dbml", engine.parse(manifest, **kwargs))
