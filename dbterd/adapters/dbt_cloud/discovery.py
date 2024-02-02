from dbterd.adapters.dbt_cloud.graphql import GraphQLHelper
from dbterd.adapters.dbt_cloud.query import Query


class DbtCloudMetadata:
    def __init__(self, **kwargs) -> None:
        self.graphql = GraphQLHelper(**kwargs)
        self.env_id = kwargs.get("dbt_cloud_environment_id")
        self.erd_query = Query().take(file_path=kwargs.get("dbt_cloud_query_file_path", None))

    def query_erd_data(self, page_size: int = 500, poll_until_end: bool = True):
        variables = {
            "environment_id": self.env_id,
            "model_first": page_size,
            "model_after": None,
            "source_first": page_size,
            "source_after": None,
            "exposure_first": page_size,
            "exposure_after": None,
            "tests_first": page_size,
            "test_after": None,
        }
        data = self.graphql.query(query=self.erd_query, **variables)
        if not poll_until_end:
            return data

        # check if hasData
        # query and merge to data

        return data
