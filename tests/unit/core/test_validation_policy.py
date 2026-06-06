from unittest import mock

import pytest

from dbterd.core import validation_policy

# Importing file.py registers the built-in relax policies as an import side effect.
from dbterd.helpers import file  # noqa: F401


@pytest.fixture
def reset_discovery():
    """Reset the once-per-process discovery guard so a test can drive it fresh."""
    original = validation_policy._EXTERNAL_POLICIES_LOADED[0]
    validation_policy._EXTERNAL_POLICIES_LOADED[0] = False
    yield
    validation_policy._EXTERNAL_POLICIES_LOADED[0] = original
    validation_policy._RELAX_POLICIES.pop("external_test_policy", None)


def _make_entry_point(name, side_effect=None):
    ep = mock.Mock()
    ep.name = name
    if side_effect is not None:
        ep.load.side_effect = side_effect
    return ep


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

    def test_register_overwrite_warns(self):
        def _first(_module):
            return None

        def _second(_module):
            return None

        validation_policy.register_relax_policy("dummy_overwrite")(_first)
        with mock.patch.object(validation_policy.logger, "warning") as mock_warning:
            validation_policy.register_relax_policy("dummy_overwrite")(_second)
        mock_warning.assert_called_once()
        assert "already registered" in mock_warning.call_args.args[0]
        assert validation_policy.get_relax_policy("dummy_overwrite") is _second
        validation_policy._RELAX_POLICIES.pop("dummy_overwrite", None)

    def test_register_same_func_twice_does_not_warn(self):
        def _same(_module):
            return None

        validation_policy.register_relax_policy("dummy_idempotent")(_same)
        with mock.patch.object(validation_policy.logger, "warning") as mock_warning:
            validation_policy.register_relax_policy("dummy_idempotent")(_same)
        mock_warning.assert_not_called()
        validation_policy._RELAX_POLICIES.pop("dummy_idempotent", None)


class TestExternalPolicyDiscovery:
    def test_ensure_policies_loaded_loads_entry_points(self, reset_discovery):
        def _register(_ep_self=None):
            validation_policy.register_relax_policy("external_test_policy")(lambda _m: None)

        ep = _make_entry_point("external_test_policy")
        ep.load.side_effect = _register

        with mock.patch.object(validation_policy, "_iter_relax_policy_entry_points", return_value=[ep]):
            validation_policy.ensure_policies_loaded()

        ep.load.assert_called_once()
        assert "external_test_policy" in validation_policy.known_relax_policies()

    def test_ensure_policies_loaded_runs_once(self, reset_discovery):
        with mock.patch.object(validation_policy, "_iter_relax_policy_entry_points", return_value=[]) as mock_iter:
            validation_policy.ensure_policies_loaded()
            validation_policy.ensure_policies_loaded()
        mock_iter.assert_called_once()

    def test_ensure_policies_loaded_skips_broken_entry_point(self, reset_discovery):
        ep = _make_entry_point("broken_policy", side_effect=ImportError("boom"))
        with (
            mock.patch.object(validation_policy, "_iter_relax_policy_entry_points", return_value=[ep]),
            mock.patch.object(validation_policy.logger, "warning") as mock_warning,
        ):
            validation_policy.ensure_policies_loaded()
        mock_warning.assert_called_once_with("Failed to load external relax policy entry point '%s'", "broken_policy")

    def test_iter_entry_points_legacy_python_fallback(self):
        legacy_eps = mock.Mock()
        legacy_eps.get.return_value = ["sentinel"]
        with mock.patch(
            "dbterd.core.validation_policy.importlib.metadata.entry_points",
            side_effect=[TypeError("no kwargs"), legacy_eps],
        ):
            result = validation_policy._iter_relax_policy_entry_points()
        assert result == ["sentinel"]
        legacy_eps.get.assert_called_once_with(validation_policy.RELAX_POLICY_ENTRY_POINT_GROUP, [])

    def test_get_relax_policy_triggers_discovery(self, reset_discovery):
        def _register(_ep_self=None):
            validation_policy.register_relax_policy("external_test_policy")(lambda _m: None)

        ep = _make_entry_point("external_test_policy")
        ep.load.side_effect = _register

        with mock.patch.object(validation_policy, "_iter_relax_policy_entry_points", return_value=[ep]):
            resolved = validation_policy.get_relax_policy("external_test_policy")
        assert callable(resolved)
