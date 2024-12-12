from typing import Optional, Tuple
import json

from dbterd.adapters import adapter
from dbterd.types import Catalog, Manifest



def run(manifest: Manifest, catalog: Catalog, **kwargs) -> Tuple[str, str]:
    """Parse dbt artifacts and export Mermaid file

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        Tuple(str, str): File name and the Mermaid content
    """
    output_file_name = kwargs.get("output_file_name") or "output.json"
    return (output_file_name, parse(manifest, catalog, **kwargs))


def parse(manifest: Manifest, catalog: Catalog, **kwargs) -> str:
    """Get the DBML content from dbt artifacts

    Args:
        manifest (dict): Manifest json
        catalog (dict): Catalog json

    Returns:
        str: JSON content
    """
    algo_module = adapter.load_algo(name=kwargs["algo"])
    tables, relationships = algo_module.parse(
        manifest=manifest, catalog=catalog, **kwargs
    )

    json_data = {"tables": {}, "relationships": []}
    for table in tables:
        json_data["tables"][table.name] = {"columns": [{"name": x.name, "type": x.data_type} for x in table.columns]}


    for rel in relationships:
        json_data["relationships"].append({
            "from": rel.table_map[1],
            "to": rel.table_map[0],
            "type": rel.type
        })

    return json.dumps(json_data, indent=4)