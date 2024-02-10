from unittest import mock

import pytest

from dbterd.adapters.dbt_cloud.graphql import GraphQLHelper


class MockResponse:
    def __init__(self, status_code, data=None) -> None:
        self.status_code = status_code
        self.data = data

    def json(self):
        return dict(data=self.data)


class TestGraphQL:
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                dict(),
                dict(host_url=None, service_token=None),
            ),
            (
                dict(dbt_cloud_host_url="host_url", dbt_cloud_service_token="token"),
                dict(host_url="host_url", service_token="token"),
            ),
        ],
    )
    def test_init(self, kwargs, expected):
        helper = GraphQLHelper(**kwargs)
        assert vars(helper) == expected
        assert helper.request_headers == {
            "authorization": f"Bearer {helper.service_token}",
            "content-type": "application/json",
        }
        assert helper.api_endpoint == f"https://{helper.host_url}/graphql/"

    @mock.patch("dbterd.adapters.dbt_cloud.administrative.requests.post")
    def test_query(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(status_code=200, data={})
        assert {} == GraphQLHelper().query(query="irrelevant", **dict())
        assert mock_requests_post.call_count == 1

    @mock.patch("dbterd.adapters.dbt_cloud.administrative.requests.post")
    def test_query_failed(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(
            status_code="irrelevant", data={}
        )
        assert GraphQLHelper().query(query="irrelevant", **dict()) is None
        assert mock_requests_post.call_count == 1

    @mock.patch("dbterd.adapters.dbt_cloud.administrative.requests.post")
    def test_query_with_exception(self, mock_requests_post):
        mock_requests_post.side_effect = Exception("any error")
        assert GraphQLHelper().query(query="irrelevant", **dict()) is None
        assert mock_requests_post.call_count == 1
