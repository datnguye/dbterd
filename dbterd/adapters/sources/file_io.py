import json

from dbt_artifacts_parser import parser


def open_json(fp):
    with open(fp, "r") as fp:
        return json.load(fp)


def read_manifest(manifest_path: str, manifest_version: int):
    manifest_dict = open_json(f"{manifest_path}/manifest.json")
    parser_version = (
        f"parse_manifest_v{manifest_version}" if manifest_version else "parse_manifest"
    )
    parse_func = getattr(parser, parser_version)
    manifest_obj = parse_func(manifest=manifest_dict)
    return manifest_obj


def read_catalog(catalog_path):
    catalog_dict = open_json(f"{catalog_path}/catalog.json")
    return parser.parse_catalog(catalog=catalog_dict)
