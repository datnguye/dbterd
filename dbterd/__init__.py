"""dbterd package initialization."""

import warnings


# Suppress the pydantic warning from the dbt-artifacts-parser dependency
warnings.filterwarnings(
    "ignore",
    message=r"Field \"model_unique_id\" in (ParsedMetric|Metric) has conflict with protected namespace \"model_\"",
    module="pydantic",
)
