from dbterd.adapters.targets.constants import Strategies
from dbterd.adapters.targets.default import default
from dbterd.adapters.targets.mermaid import mermaid_test_relationship

run_operation_default = default
run_operation_dispatcher = {
    Strategies.MERMAID_TEST_RELATIONSHIP: mermaid_test_relationship.run,
}
