import json
from unittest import mock

import pytest
import requests

from dbterd.plugins.dbt_cloud.administrative import DbtCloudArtifact


class MockResponse:
    def __init__(self, status_code, data=None) -> None:
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data


class TestDbtCloudArtifact:
    @pytest.fixture
    def dbt_cloud_artifact(self) -> DbtCloudArtifact:
        return DbtCloudArtifact(
            dbt_cloud_host_url="irrelevant_url",
            dbt_cloud_service_token="irrelevant_st",
            dbt_cloud_account_id="irrelevant_acc_id",
            dbt_cloud_run_id="irrelevant_run_id",
            dbt_cloud_api_version="irrelevant_v",
        )

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {"dbt_cloud_run_id": "run_id"},
                {
                    "host_url": None,
                    "service_token": None,
                    "account_id": None,
                    "run_id": "run_id",
                    "job_id": None,
                    "api_version": None,
                },
            ),
            (
                {
                    "dbt_cloud_host_url": "host_url",
                    "dbt_cloud_service_token": "service_token",
                    "dbt_cloud_account_id": "account_id",
                    "dbt_cloud_run_id": "run_id",
                    "dbt_cloud_api_version": "api_version",
                },
                {
                    "host_url": "host_url",
                    "service_token": "service_token",
                    "account_id": "account_id",
                    "run_id": "run_id",
                    "job_id": None,
                    "api_version": "api_version",
                },
            ),
        ],
    )
    def test_init_run(self, kwargs, expected):
        dbt_cloud = DbtCloudArtifact(**kwargs)
        assert vars(dbt_cloud) == expected
        assert dbt_cloud.request_headers == {"Authorization": f"Token {kwargs.get('dbt_cloud_service_token')}"}
        assert dbt_cloud.api_endpoint == (
            "https://{host_url}/api/{api_version}/accounts/{account_id}/runs/{run_id}/artifacts/{{path}}"
        ).format(**expected)
        assert dbt_cloud.manifest_api_endpoint == (
            "https://{host_url}/api/{api_version}/accounts/{account_id}/runs/{run_id}/artifacts/manifest.json"
        ).format(**expected)
        assert dbt_cloud.catalog_api_endpoint == (
            "https://{host_url}/api/{api_version}/accounts/{account_id}/runs/{run_id}/artifacts/catalog.json"
        ).format(**expected)

    @pytest.mark.parametrize(
        "kwargs, endpoint",
        [
            (
                {"dbt_cloud_run_id": "run_id"},
                "https://None/api/None/accounts/None/runs/run_id/artifacts/{path}",
            ),
            (
                {"dbt_cloud_run_id": "run_id", "dbt_cloud_job_id": "job_id"},
                "https://None/api/None/accounts/None/runs/run_id/artifacts/{path}",
            ),
            (
                {"dbt_cloud_job_id": "job_id"},
                "https://None/api/None/accounts/None/jobs/job_id/artifacts/{path}",
            ),
        ],
    )
    def test_api_endpoint(self, kwargs, endpoint):
        dbt_cloud = DbtCloudArtifact(**kwargs)
        assert dbt_cloud.api_endpoint == endpoint

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.file.write_json")
    @mock.patch("dbterd.plugins.dbt_cloud.administrative.requests.get")
    def test_download_artifact_ok(self, mock_requests_get, mock_write_json, dbt_cloud_artifact):
        mock_requests_get.return_value = MockResponse(status_code=200, data={})
        assert dbt_cloud_artifact.download_artifact(artifact="manifest", artifacts_dir="/irrelevant/path")
        mock_write_json.assert_called_once_with(
            data=json.dumps({}, indent=2),
            path="/irrelevant/path/manifest.json",
        )

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.file.write_json")
    def test_download_artifact_bad_parameters(self, mock_write_json, dbt_cloud_artifact):
        with pytest.raises(AttributeError):
            dbt_cloud_artifact.download_artifact(artifact="irrelevant", artifacts_dir="/irrelevant/path")
        assert mock_write_json.call_count == 0

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.file.write_json")
    @mock.patch("dbterd.plugins.dbt_cloud.administrative.requests.get")
    def test_download_artifact_network_failed(self, mock_requests_get, mock_write_json, dbt_cloud_artifact):
        mock_requests_get.side_effect = requests.exceptions.ConnectionError()
        assert not dbt_cloud_artifact.download_artifact(artifact="manifest", artifacts_dir="/irrelevant/path")
        assert mock_write_json.call_count == 0

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.file.write_json")
    @mock.patch("dbterd.plugins.dbt_cloud.administrative.requests.get")
    def test_download_artifact_failed_to_save_file(self, mock_requests_get, mock_write_json, dbt_cloud_artifact):
        mock_requests_get.return_value = MockResponse(status_code=200, data={})
        mock_write_json.side_effect = OSError("any error")
        assert not dbt_cloud_artifact.download_artifact(artifact="manifest", artifacts_dir="/irrelevant/path")
        assert mock_write_json.call_count == 1

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.file.write_json")
    @mock.patch("dbterd.plugins.dbt_cloud.administrative.requests.get")
    def test_download_artifact_status_not_ok(self, mock_requests_get, mock_write_json, dbt_cloud_artifact):
        mock_requests_get.return_value = MockResponse(status_code=999)
        assert not dbt_cloud_artifact.download_artifact(artifact="manifest", artifacts_dir="/irrelevant/path")
        assert mock_write_json.call_count == 0

    @mock.patch("dbterd.plugins.dbt_cloud.administrative.DbtCloudArtifact.download_artifact")
    def test_get(self, mock_download_artifact, dbt_cloud_artifact):
        mock_download_artifact.return_value = True
        assert dbt_cloud_artifact.get(artifacts_dir="/irrelevant/path")
        assert mock_download_artifact.call_count == 2
