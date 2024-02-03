import os

from dbterd.helpers.log import logger


class Query:
    """ERD Query file helper"""

    def __init__(self) -> None:
        """Initilize the required input:
        - Query directory
        """
        self.dir = f"{os.path.dirname(os.path.realpath(__file__))}/include"

    def take(self, file_path: str = None) -> str:
        """Read the given file path and return the content as the query string

        Args:
            file_path (str, optional): File path. Defaults to `(query dir)/erd_query.gql`

        Returns:
            str: Query string
        """
        query_file = file_path or f"{self.dir}/erd_query.gql"
        logger.info(f"Looking for the query in: {query_file}")
        return self.get_file_content(file_path=query_file)

    def get_file_content(self, file_path: str) -> str:
        """Read content of the given file path

        Args:
            file_path (str): Query file path

        Returns:
            str: Query string
        """
        try:
            with open(file_path, "r") as content:
                return content.read()
        except Exception as e:
            logger.error(f"Cannot read file: [{file_path}] with error: {str(e)}")
            return None
