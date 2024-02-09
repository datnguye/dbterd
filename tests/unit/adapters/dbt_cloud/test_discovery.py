from unittest import mock

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

    @pytest.mark.parametrize(
        "graphql_query_data, extract_data",
        [
            ({}, [{}]),
            (
                dict(
                    environment=dict(
                        applied=dict(
                            models=dict(edges=[]),
                            sources=dict(edges=[]),
                            exposures=dict(edges=[]),
                            tests=dict(edges=[]),
                        )
                    )
                ),
                [
                    dict(
                        models=dict(edges=[]),
                        sources=dict(edges=[]),
                        exposures=dict(edges=[]),
                        tests=dict(edges=[]),
                    )
                ],
            ),
        ],
    )
    @mock.patch("dbterd.adapters.dbt_cloud.graphql.GraphQLHelper.query")
    def test_query_erd_data(self, mock_graphql_query, graphql_query_data, extract_data):
        mock_graphql_query.return_value = graphql_query_data
        assert extract_data == DbtCloudMetadata().query_erd_data()
        assert mock_graphql_query.call_count == len(extract_data)

    @mock.patch("dbterd.adapters.dbt_cloud.graphql.GraphQLHelper.query")
    def test_query_erd_data_no_polling(self, mock_graphql_query):
        mock_graphql_query.return_value = {}
        assert [{}] == DbtCloudMetadata().query_erd_data(poll_until_end=False)
        assert mock_graphql_query.call_count == 1

    @mock.patch("dbterd.adapters.dbt_cloud.graphql.GraphQLHelper.query")
    def test_query_erd_data_polling_twice(self, mock_graphql_query):
        mock_graphql_query.side_effect = [
            dict(
                environment=dict(
                    applied=dict(
                        models=dict(edges=[], pageInfo=dict(hasNextPage=True)),
                        sources=dict(edges=[]),
                        exposures=dict(edges=[]),
                        tests=dict(edges=[]),
                    )
                )
            ),
            dict(
                environment=dict(
                    applied=dict(
                        models=dict(edges=[]),
                        sources=dict(edges=[]),
                        exposures=dict(edges=[]),
                        tests=dict(edges=[]),
                    )
                )
            ),
        ]
        assert [
            dict(
                models=dict(edges=[], pageInfo=dict(hasNextPage=True)),
                sources=dict(edges=[]),
                exposures=dict(edges=[]),
                tests=dict(edges=[]),
            ),
            dict(
                models=dict(edges=[]),
                sources=dict(edges=[]),
                exposures=dict(edges=[]),
                tests=dict(edges=[]),
            ),
        ] == DbtCloudMetadata().query_erd_data()
        assert mock_graphql_query.call_count == 2
