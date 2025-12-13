from dbterd.plugins.dbt_cloud.query import Query


class TestQuery:
    def test_get_file_content_error(self):
        assert Query().get_file_content(file_path="invalid-file-path") is None
