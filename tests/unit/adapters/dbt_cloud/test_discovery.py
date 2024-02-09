import pytest

from dbterd.adapters.dbt_cloud.discovery import DbtCloudMetadata


class TestDbtCloudMetadata:
    @pytest.fixture
    def dbtCloudMetadata(self) -> DbtCloudMetadata:
        return DbtCloudMetadata(
            dbt_cloud_host_url="irrelevant_url",
            dbt_cloud_service_token="irrelevant_st",
            dbt_cloud_environment_id="irrelevant_env_id",
            dbt_cloud_query_file_path="irrelevant_query_file_path",
        )

    def test_init(self):
        pass
