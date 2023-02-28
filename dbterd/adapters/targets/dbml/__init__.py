from dbterd.adapters.targets.dbml.constants import Strategies
from dbterd.adapters.targets.dbml.strategies import dbml_test_relationship, default

operation_default = default.default
run_operation_dispatcher = {
    Strategies.DBML_TEST_RELATIONSHIP: dbml_test_relationship.run,
}
