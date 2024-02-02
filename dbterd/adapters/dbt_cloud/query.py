import os

from dbterd.helpers.log import logger


class Query:
    def __init__(self) -> None:
        self.dir = f"{os.path.dirname(os.path.realpath(__file__))}/include"

    def take(self, file_path: str = None) -> str:
        query_file = file_path or f"{self.dir}/erd_query.gql"
        logger.info(f"Looking for the query in: {query_file}")
        return self.get_file_content(file_path=query_file)

    def get_file_content(self, file_path: str):
        try:
            with open(file_path, "r") as content:
                return content.read()
        except Exception as e:
            logger.error(f"Cannot read file: [{file_path}] with error: {str(e)}")
            return None
