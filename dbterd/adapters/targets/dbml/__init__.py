import os
from dbterd.adapters.targets.dbml.contants import Strategies
from dbterd.adapters.targets.dbml.strategies import default
from dbterd.adapters.targets.dbml.strategies import dbml_test_relationship

operation_default = default.default
run_operation_dispatcher = {
    Strategies.DBML_TEST_RELATIONSHIP: dbml_test_relationship.run,
}
