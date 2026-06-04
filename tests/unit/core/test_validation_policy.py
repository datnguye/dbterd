import pytest

from dbterd.core import validation_policy

# Importing file.py registers the built-in relax policies as an import side effect.
from dbterd.helpers import file  # noqa: F401


class TestValidationPolicyRegistry:
    def test_known_relax_policies_includes_builtins(self):
        known = validation_policy.known_relax_policies()
        assert "relax_extra_fields" in known
        assert "relax_enum_values" in known

    def test_known_relax_policies_is_sorted(self):
        known = validation_policy.known_relax_policies()
        assert list(known) == sorted(known)

    def test_register_and_resolve_roundtrip(self):
        @validation_policy.register_relax_policy("dummy_policy_for_test")
        def _dummy(_module):
            return None

        assert validation_policy.get_relax_policy("dummy_policy_for_test") is _dummy
        # Cleanup so the test registry stays clean for other tests.
        validation_policy._RELAX_POLICIES.pop("dummy_policy_for_test", None)

    def test_get_relax_policy_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown validation policy 'does_not_exist'"):
            validation_policy.get_relax_policy("does_not_exist")
