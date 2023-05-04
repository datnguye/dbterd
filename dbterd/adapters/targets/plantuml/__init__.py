from dbterd.adapters.targets.constants import Strategies
from dbterd.adapters.targets.default import default
from dbterd.adapters.targets.plantuml import plantuml_test_relationship

run_operation_default = default
run_operation_dispatcher = {
    Strategies.PLANTUML_TEST_RELATIONSHIP: plantuml_test_relationship.run,
}
