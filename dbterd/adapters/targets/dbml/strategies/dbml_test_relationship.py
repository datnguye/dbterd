from dbterd.adapters.targets.dbml.engine import engine


def run(manifest):
    return ("output.dbml", engine.parse(manifest=manifest))
