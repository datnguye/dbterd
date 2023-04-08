from dbterd.adapters.targets.constants import Strategies
from dbterd.adapters.targets.dbml import dbml_test_relationship
from dbterd.adapters.targets.default import default

run_operation_default = default
run_operation_dispatcher = {
    Strategies.DBML_TEST_RELATIONSHIP: dbml_test_relationship.run,
}
