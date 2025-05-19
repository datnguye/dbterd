"""Configuration settings for dbterd."""

from pydantic import ConfigDict


# This is used to suppress warnings about model_unique_id field in dbt-artifacts-parser
model_config = ConfigDict(protected_namespaces=())
