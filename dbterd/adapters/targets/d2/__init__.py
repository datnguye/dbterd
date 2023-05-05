from dbterd.adapters.targets.constants import Strategies
from dbterd.adapters.targets.d2 import d2_test_relationship
from dbterd.adapters.targets.default import default

run_operation_default = default
run_operation_dispatcher = {
    Strategies.D2_TEST_RELATIONSHIP: d2_test_relationship.run,
}
