import json
import os
import subprocess

from dbterd.adapters.targets.json import get_schema_version
from dbterd.core.schemas.erd import build_erd_json_schema


def _write_erd_schema(site_dir: str) -> None:
    """Publish the dbterd ERD JSON Schema, versioned plus a `latest` alias.

    A stable, citable URL per version so downstream tools can pin to exactly
    the contract they were built against.
    """
    schema_root = os.path.join(site_dir, "schemas", "erd")
    for version_segment in {get_schema_version(), "latest"}:
        version_dir = os.path.join(schema_root, version_segment)
        os.makedirs(version_dir, exist_ok=True)
        schema = build_erd_json_schema(version_segment)
        with open(os.path.join(version_dir, "erd.json"), "w", encoding="utf-8") as handle:
            json.dump(schema, handle, indent=2)
            handle.write("\n")


def on_post_build(config, **kwargs):
    site_dir = config["site_dir"]
    subprocess.run(["pdoc", "-t", "docs/assets/css", "dbterd/api/", "-o", f"{site_dir}/api-docs"], check=False)
    _write_erd_schema(site_dir)
