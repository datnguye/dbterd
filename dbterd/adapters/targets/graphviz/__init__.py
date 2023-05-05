from dbterd.adapters.targets.constants import Strategies
from dbterd.adapters.targets.default import default
from dbterd.adapters.targets.graphviz import graphviz_test_relationship

run_operation_default = default
run_operation_dispatcher = {
    Strategies.GRAPHVIZ_TEST_RELATIONSHIP: graphviz_test_relationship.run,
}
