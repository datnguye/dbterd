import os
import json

import requests

from dbterd.helpers import file
from dbterd.helpers.log import logger


class DbtCloudArtifact:
    """dbt Cloud Artifact class using
    dbt CLoud Administrative API
    https://docs.getdbt.com/docs/dbt-cloud-apis/admin-cloud-api.

    And use Retrieve Run Artifact endpoint, for example, with v2 spec
    https://docs.getdbt.com/dbt-cloud/api-v2#/operations/Retrieve%20Run%20Artifact
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the base attributes to interact with API service

        Passing JOB_ID to get the latest run's artifacts. In particular to a run, let's use RUN_ID.
        RUN_ID will take the precedence if specified
        """
        self.host_url = kwargs.get("dbt_cloud_host_url")
        self.service_token = kwargs.get("dbt_cloud_service_token")
        self.account_id = kwargs.get("dbt_cloud_account_id")
        self.job_id = kwargs.get("dbt_cloud_job_id")
        self.run_id = kwargs.get("dbt_cloud_run_id")
        self.api_version = kwargs.get("dbt_cloud_api_version")

    @property
    def request_headers(self) -> dict:
        """API Header"""
        return {"Authorization": f"Token {self.service_token}"}

    @property
    def api_endpoint(self) -> dict:
        """Base API endpoint to a specific artifact object"""
        return (
            "https://{host_url}/api/{api_version}/"
            "accounts/{account_id}/"
            "{artifact_id}/"
            "artifacts/{{path}}"
        ).format(
            host_url=self.host_url,
            api_version=self.api_version,
            account_id=self.account_id,
            artifact_id=f"runs/{self.run_id}" if self.run_id else f"jobs/{self.job_id}",
        )

    @property
    def manifest_api_endpoint(self) -> dict:
        """Full API endpoint to the `manifest.json` file"""
        return self.api_endpoint.format(path="manifest.json")

    @property
    def catalog_api_endpoint(self) -> dict:
        """Full API endpoint to the `catalog.json` file"""
        return self.api_endpoint.format(path="catalog.json")

    def download_artifact(self, artifact: str, artifacts_dir: str) -> bool:
        """Request API to download the artifact file

        Args:
            artifact (str): The artifact name e.g. manifest or catalog

        Returns:
            bool: True is success, False if any errors
        """
        artifact_api_endpoint = getattr(self, f"{artifact}_api_endpoint")
        logger.debug(f"Dowloading...[URL: {artifact_api_endpoint}]")
        try:
            r = requests.get(url=artifact_api_endpoint, headers=self.request_headers)
            logger.debug(f"Completed [status: {r.status_code}]")

            if r.status_code != 200:
                logger.error(f"Failed to retrieve artifacts [error: {vars(r)}]")
                return False

            file.write_json(
                data=json.dumps(r.json(), indent=2),
                path=f"{artifacts_dir}/{artifact}.json",
            )
        except Exception as e:
            logger.error(f"Error occurred while downloading [error: {str(e)}]")
            return False

        return True

    def get(self, artifacts_dir: str = None) -> bool:
        """Download `manifest.json` and `catalog.json` to the local dir

        Args:
            artifacts_dir (str, optional): Local dir where the artifacts get downloaded to. Default to CWD/target.

        Returns:
            bool: True is success, False if any errors
        """
        _artifacts_dir = artifacts_dir or f"{os.getcwd()}/target"
        r = self.download_artifact(artifact="manifest", artifacts_dir=_artifacts_dir)
        if r:
            r = self.download_artifact(artifact="catalog", artifacts_dir=_artifacts_dir)

        return r
