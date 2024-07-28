from dataclasses import dataclass, field


@dataclass
class DummyManifestV6:
    compiled_sql: str = "compiled_sql"


@dataclass
class DummyManifestV7:
    compiled_code: str = "compiled_code"


@dataclass
class DummyManifestError:
    raw_sql: str = "raw_sql"


@dataclass
class DummyManifestHasColumns:
    columns = dict({"col1": None, "col2": None})
    database = "database_dummy"
    schema = "schema_dummy"


@dataclass
class ManifestNodeTestMetaData:
    kwargs: dict


@dataclass
class ManifestNodeDependsOn:
    nodes: list = field(default_factory=list)


@dataclass
class ManifestNode:
    test_metadata: ManifestNodeTestMetaData
    meta: dict
    columns: dict
    raw_sql: str = ""
    database: str = ""
    schema_: str = ""
    depends_on: ManifestNodeDependsOn = field(default_factory=ManifestNodeDependsOn)
    description: str = ""


@dataclass
class SemanticModelEntityType:
    value: str


@dataclass
class SemanticModelEntity:
    name: str
    type: SemanticModelEntityType
    expr: str


@dataclass
class NodeConfig:
    meta: dict = field(default_factory=dict)


@dataclass
class SemanticModel:
    entities: list = field(default_factory=list)
    depends_on: ManifestNodeDependsOn = field(default_factory=ManifestNodeDependsOn)
    primary_entity: str = None
    config: NodeConfig = field(default_factory=NodeConfig)


@dataclass
class ManifestExposureNode:
    depends_on: ManifestNodeDependsOn


@dataclass
class ManifestNodeColumn:
    name: str
    data_type: str = "unknown"
    description: str = ""


@dataclass
class DummyManifestRel:
    semantic_models = {
        "semantic_model.dbt_resto.sm1": SemanticModel(
            entities=[
                SemanticModelEntity(
                    name="id1", type=SemanticModelEntityType(value="primary"), expr=None
                )
            ],
            depends_on=ManifestNodeDependsOn(nodes=["model.dbt_resto.table1"]),
            primary_entity=None,
        ),
        "semantic_model.dbt_resto.sm2": SemanticModel(
            entities=[
                SemanticModelEntity(
                    name="id1",
                    type=SemanticModelEntityType(value="foreign"),
                    expr="id2",
                )
            ],
            depends_on=ManifestNodeDependsOn(nodes=["model.dbt_resto.table2"]),
            primary_entity="id2",
        ),
        "semantic_model.dbt_resto.smx": SemanticModel(
            entities=[
                SemanticModelEntity(
                    name="pkx", type=SemanticModelEntityType(value="primary"), expr=None
                ),
                SemanticModelEntity(
                    name="id1", type=SemanticModelEntityType(value="foreign"), expr="x"
                ),
            ],
            depends_on=ManifestNodeDependsOn(nodes=["model.dbt_resto.tablex"]),
            primary_entity=None,
        ),
    }
    nodes = {
        "test.dbt_resto.relationships_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table2": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table3": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('tabley')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.tabley", "model.dbt_resto.tablex"]
            ),
        ),
        "test.dbt_resto.relationships_tablex": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "x", "field": "y", "to": "ref('y')"}
            ),
            meta={"ignore_in_erd": 1},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.y", "model.dbt_resto.x"]
            ),
        ),
        "test.dbt_resto.foreign_key_table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={
                    "column_name": "f1",
                    "pk_column_name": "f2",
                    "pk_table_name": "ref('table2')",
                }
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table2", "model.dbt_resto.table1"]
            ),
        ),
        "test.dbt_resto.relationships_table4": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table-m2')"}
            ),
            meta={"relationship_type": "one-to-one"},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table-m2", "model.dbt_resto.table-m1"]
            ),
        ),
        "test.dbt_resto.relationships_table1_reverse": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table-r2')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table-r1", "model.dbt_resto.table-r2"]
            ),
        ),
        "test.dbt_resto.relationships_table1_recursive": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(
                kwargs={"column_name": "f1", "field": "f2", "to": "ref('table1')"}
            ),
            meta={},
            columns={},
            depends_on=ManifestNodeDependsOn(nodes=["model.dbt_resto.table1"]),
        ),
    }


@dataclass
class DummyManifestTable:
    nodes = {
        "model.dbt_resto.table1": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql--",
            database="--database--",
            schema_="--schema--",
            columns={},
        ),
        "model.dbt_resto.table_dummy_columns": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql--",
            database="--database--",
            schema_="--schema--",
            columns={},
        ),
        "model.dbt_resto.table2": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            raw_sql="--raw_sql2--",
            database="--database2--",
            schema_="--schema2--",
            columns={
                "name2": ManifestNodeColumn(name="name2"),
                "name3": ManifestNodeColumn(name="name3"),
            },
        ),
    }
    sources = {
        "source.dummy.source_table": ManifestNode(
            test_metadata=ManifestNodeTestMetaData(kwargs={}),
            meta={},
            database="--database--",
            schema_="--schema--",
            columns={
                "name1": ManifestNodeColumn(name="name1"),
                "name2": ManifestNodeColumn(name="name2"),
            },
        ),
    }


@dataclass
class DummyManifestWithExposure:
    exposures = {
        "exposure.dbt_resto.dummy": ManifestExposureNode(
            depends_on=ManifestNodeDependsOn(
                nodes=["model.dbt_resto.table1", "model.dbt_resto.table2"]
            ),
        )
    }


@dataclass
class CatalogNode:
    columns: dict


@dataclass
class CatalogNodeColumn:
    type: str
    comment: str = ""


@dataclass
class DummyCatalogTable:
    nodes = {
        "model.dbt_resto.table1": CatalogNode(
            columns={"name1": CatalogNodeColumn(type="--name1-type--")}
        ),
        "model.dbt_resto.table2": CatalogNode(
            columns={"name3": CatalogNodeColumn(type="--name3-type--")}
        ),
    }
    sources = {
        "source.dummy.source_table": CatalogNode(
            columns={"name1": CatalogNodeColumn(type="--name1-type--")}
        ),
    }
