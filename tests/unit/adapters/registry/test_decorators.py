from dbterd.core.registry.decorators import (
    ALGORITHM_REGISTRY_NAME,
    TARGET_REGISTRY_NAME,
    register_algorithm,
    register_target,
)


class TestRegisterAlgorithm:
    def test_register_algorithm_with_explicit_name(self):
        """Test registering algorithm with explicit name."""

        @register_algorithm("custom_name")
        class TestAlgo:
            pass

        assert hasattr(TestAlgo, ALGORITHM_REGISTRY_NAME)
        assert getattr(TestAlgo, ALGORITHM_REGISTRY_NAME) == "custom_name"

    def test_register_algorithm_with_name_property(self):
        """Test registering algorithm that has a name property."""

        @register_algorithm()
        class TestAlgo:
            @property
            def name(self) -> str:
                return "algo_from_property"

        assert hasattr(TestAlgo, ALGORITHM_REGISTRY_NAME)
        assert getattr(TestAlgo, ALGORITHM_REGISTRY_NAME) == "algo_from_property"

    def test_register_algorithm_without_name_property(self):
        """Test registering algorithm without name property falls back to class name."""

        @register_algorithm()
        class TestAlgoClass:
            pass

        assert hasattr(TestAlgoClass, ALGORITHM_REGISTRY_NAME)
        assert getattr(TestAlgoClass, ALGORITHM_REGISTRY_NAME) == "testalgoclass"

    def test_register_algorithm_with_broken_name_property(self):
        """Test registering algorithm when name property raises exception."""

        @register_algorithm()
        class TestAlgo:
            def __init__(self):
                raise RuntimeError("Cannot instantiate")

            @property
            def name(self) -> str:
                return "should_not_reach_here"

        assert hasattr(TestAlgo, ALGORITHM_REGISTRY_NAME)
        assert getattr(TestAlgo, ALGORITHM_REGISTRY_NAME) == "testalgo"


class TestRegisterTarget:
    def test_register_target_with_explicit_name(self):
        """Test registering target with explicit name."""

        @register_target("custom_target")
        class TestTarget:
            pass

        assert hasattr(TestTarget, TARGET_REGISTRY_NAME)
        assert getattr(TestTarget, TARGET_REGISTRY_NAME) == "custom_target"

    def test_register_target_with_name_property(self):
        """Test registering target that has a name property."""

        @register_target()
        class TestTarget:
            @property
            def name(self) -> str:
                return "target_from_property"

        assert hasattr(TestTarget, TARGET_REGISTRY_NAME)
        assert getattr(TestTarget, TARGET_REGISTRY_NAME) == "target_from_property"

    def test_register_target_without_name_property(self):
        """Test registering target without name property falls back to class name."""

        @register_target()
        class TestTargetClass:
            pass

        assert hasattr(TestTargetClass, TARGET_REGISTRY_NAME)
        assert getattr(TestTargetClass, TARGET_REGISTRY_NAME) == "testtargetclass"

    def test_register_target_with_broken_name_property(self):
        """Test registering target when name property raises exception."""

        @register_target()
        class TestTarget:
            def __init__(self):
                raise RuntimeError("Cannot instantiate")

            @property
            def name(self) -> str:
                return "should_not_reach_here"

        assert hasattr(TestTarget, TARGET_REGISTRY_NAME)
        assert getattr(TestTarget, TARGET_REGISTRY_NAME) == "testtarget"
