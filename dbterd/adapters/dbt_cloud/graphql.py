import requests

from dbterd.helpers.log import logger


class GraphQLHelper:
    """GraphQL Helper class"""

    def __init__(self, **kwargs) -> None:
        """Initilize the required inputs:
        - Host URL
        - Bearer Token
        """
        self.host_url = kwargs.get("dbt_cloud_host_url")
        self.service_token = kwargs.get("dbt_cloud_service_token")

    @property
    def request_headers(self) -> dict:
        """API Header"""
        return {
            "authorization": f"Bearer {self.service_token}",
            "content-type": "application/json",
        }

    @property
    def api_endpoint(self) -> dict:
        """Base GraphQL API endpoint"""
        return f"https://{self.host_url}/graphql/"

    def query(self, query: str, **variables):
        """POST Graph QL query

        Args:
            query (str): query string

        Returns:
            dict: Query data responsed. None if any exceptions
        """
        try:
            logger.debug(
                f"Getting erd data...[URL: {self.api_endpoint}, VARS: {variables}]"
            )
            r = requests.post(
                self.api_endpoint,
                headers=self.request_headers,
                json={"query": query, "variables": variables},
            )
            logger.debug(f"Completed [status: {r.status_code}]")

            if r.status_code != 200:
                logger.error(f"Failed to query [error: {vars(r)}]")
                return None
        except Exception as e:
            logger.error(f"Error occurred while querying [error: {str(e)}]")
            return None

        return r.json().get("data")
