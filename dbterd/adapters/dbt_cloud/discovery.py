from dbterd.adapters.dbt_cloud.graphql import GraphQLHelper
from dbterd.adapters.dbt_cloud.query import Query
from dbterd.helpers.log import logger


class DbtCloudMetadata:
    """Class for managing the Discovery API via GraphQL"""

    def __init__(self, **kwargs) -> None:
        """Initialize the GraphQL Helper and the corresponding ERD query"""
        self.graphql = GraphQLHelper(**kwargs)
        self.environment_id = kwargs.get("dbt_cloud_environment_id")
        self.erd_query = Query().take(
            file_path=kwargs.get("dbt_cloud_query_file_path", None)
        )
        self.last_cursor = {}

    def query_erd_data(self, page_size: int = 500, poll_until_end: bool = True):
        """Perform query to get the ERD dict result

        Args:
            page_size (int, optional): Pagination size. Defaults to 500.
            poll_until_end (bool, optional): Decide to pull all data. Defaults to True.

        Returns:
            list[dict]: Metadata result list
        """
        variables = {
            "environment_id": self.environment_id,
            "model_first": page_size,
            "source_first": page_size,
            "exposure_first": page_size,
            "test_first": page_size,
        }
        data = [
            self.extract_data(
                graphql_data=self.graphql.query(query=self.erd_query, **variables)
            )
        ]
        self.show_counts(data=data[-1])
        if not poll_until_end:
            return data

        while any(
            [
                self.has_data(data=data[-1], resource_type="model"),
                self.has_data(data=data[-1], resource_type="source"),
                self.has_data(data=data[-1], resource_type="exposure"),
                self.has_data(data=data[-1], resource_type="test"),
            ]
        ):
            variables["model_after"] = self.get_last_cursor(
                data=data[-1], resource_type="model"
            )
            variables["source_after"] = self.get_last_cursor(
                data=data[-1], resource_type="source"
            )
            variables["exposure_after"] = self.get_last_cursor(
                data=data[-1], resource_type="exposure"
            )
            variables["test_after"] = self.get_last_cursor(
                data=data[-1], resource_type="test"
            )

            self.save_last_cursor(data=data[-1])
            data.append(
                self.extract_data(
                    graphql_data=self.graphql.query(query=self.erd_query, **variables)
                )
            )
            self.show_counts(data=data[-1])

        return data

    def extract_data(self, graphql_data: dict):
        """Extract the core nested dict only:
        environment:
            applied: <-- HERE
                models
                sources
                tests
                exposures

        Args:
            graphql_data (dict): Metadata result

        Returns:
            dict: Applied data
        """
        return graphql_data.get("environment", {}).get("applied", {})

    def has_data(self, data, resource_type: str = "model") -> bool:
        """Check if there is still having data to poll more given the resource type.

        Resource types:
        - model
        - source
        - exposure
        - test

        Args:
            data (dict): Metadata result
            resource_type (str, optional): Resource type. Defaults to "model".

        Returns:
            bool: True if has data need polling more
        """
        return (
            data.get(f"{resource_type}s", {})
            .get("pageInfo", {})
            .get("hasNextPage", False)
        )

    def save_last_cursor(
        self, data, resource_types=["model", "source", "exposure", "test"]
    ):
        """Save last poll's cursor of all resource types.

        Args:
            data (dict): Metadata result
            resource_types (list, optional): |
                Resource types.
                Defaults to ["model", "source", "exposure", "test"].
        """
        for resource_type in resource_types:
            self.last_cursor[resource_type] = self.get_last_cursor(
                data=data, resource_type=resource_type
            ) or self.last_cursor.get(resource_type, None)

    def get_last_cursor(self, data, resource_type: str = "model") -> str:
        """Retrieve the last cursor of given resource type

        Args:
            data (dict): Metadata result
            resource_type (str, optional): Resource type. Defaults to "model".

        Returns:
            str: Cursor value
        """
        return (
            data.get(f"{resource_type}s", {}).get("pageInfo", {}).get("endCursor", None)
        ) or (self.last_cursor.get(f"{resource_type}", None))

    def get_count(self, data, resource_type: str = "model") -> int:
        """Get metadata result count of given resource type

        Args:
            data (dict):  Metadata result
            resource_type (str, optional): Resource type. Defaults to "model".

        Returns:
            int: Number of metadata nodes given resource type
        """
        return len(data.get(f"{resource_type}s", {}).get("edges", []))

    def show_counts(self, data, resource_types=["model", "source", "exposure", "test"]):
        """Print the metadata result count for all resource types

        Args:
            data (dict): Metadata result
            resource_types (list, optional): |
                Resource types.
                Defaults to ["model", "source", "exposure", "test"].
        """
        results = [
            f"{self.get_count(data=data, resource_type=x)} {x}(s)"
            for x in resource_types
        ]
        logger.info(f"Metadata result: {', '.join(results)}")
