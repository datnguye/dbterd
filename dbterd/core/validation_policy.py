"""Registry of named validation-relaxation policies.

Each policy is a function that loosens dbt-artifacts-parser Pydantic validation in a
specific way (e.g. ignore unknown fields, widen unknown enum values). Users opt in by
listing policy names in the ``relax-policies`` config; only listed policies run, so an
empty list means strict validation.

Policies come from two sources, mirroring how algo/target adapters are discovered:

1. **Built-in** policies in ``dbterd.core.relax_policies`` (registered on import).
2. **External packages** that declare entry points in the ``dbterd.relax_policies``
   group. Such a package ships a module that calls ``@register_relax_policy`` and
   points an entry point at it::

       [project.entry-points."dbterd.relax_policies"]
       relax_my_thing = "my_pkg.policies"

   The entry point just needs to be loaded — importing the module fires the decorator,
   which registers the policy. Discovery runs lazily via ``ensure_policies_loaded``.
"""

from collections.abc import Callable
import importlib
import importlib.metadata

from dbterd.helpers.log import logger


# Entry-point group external packages use to contribute relax policies.
RELAX_POLICY_ENTRY_POINT_GROUP = "dbterd.relax_policies"

# name -> relax function. Populated by @register_relax_policy.
_RELAX_POLICIES: dict[str, Callable[[object], None]] = {}

# Guards repeated entry-point scans; discovery only needs to run once per process.
# A list (not a bare bool) so ``ensure_policies_loaded`` can flip it without ``global``.
_EXTERNAL_POLICIES_LOADED: list[bool] = [False]

RelaxPolicy = Callable[[object], None]


def register_relax_policy(name: str) -> Callable[[RelaxPolicy], RelaxPolicy]:
    """Register a relaxation function under a policy name.

    Args:
        name: The policy name users reference in the ``relax-policies`` config.

    Returns:
        Decorator that records the function and returns it unchanged.

    Example:
        @register_relax_policy("relax_extra_fields")
        def relax_pydantic_models(artifact_module): ...
    """

    def decorator(func: RelaxPolicy) -> RelaxPolicy:
        if name in _RELAX_POLICIES and _RELAX_POLICIES[name] is not func:
            logger.warning("Relax policy '%s' is already registered; overwriting it.", name)
        _RELAX_POLICIES[name] = func
        return func

    return decorator


def _iter_relax_policy_entry_points():
    """Yield entry points in the ``dbterd.relax_policies`` group across Python versions."""
    try:
        return importlib.metadata.entry_points(group=RELAX_POLICY_ENTRY_POINT_GROUP)
    except TypeError:
        # Python < 3.12: entry_points() doesn't accept keyword arguments.
        return importlib.metadata.entry_points().get(RELAX_POLICY_ENTRY_POINT_GROUP, [])


def ensure_policies_loaded() -> None:
    """Discover and register external relax policies via entry points.

    Built-in policies register on import of ``dbterd.core.relax_policies``. This adds
    third-party policies declared in the ``dbterd.relax_policies`` entry-point group:
    each entry point is loaded, which imports the target module and fires its
    ``@register_relax_policy`` decorators. The scan runs at most once per process.

    A failing external policy is logged and skipped — a broken third-party plugin must
    not prevent dbterd from reading artifacts with the built-in policies.
    """
    if _EXTERNAL_POLICIES_LOADED[0]:
        return
    _EXTERNAL_POLICIES_LOADED[0] = True

    for ep in _iter_relax_policy_entry_points():
        try:
            ep.load()
        except (ImportError, AttributeError):
            logger.warning("Failed to load external relax policy entry point '%s'", ep.name)


def get_relax_policy(name: str) -> RelaxPolicy:
    """Resolve a policy name to its relax function.

    Args:
        name: The configured policy name.

    Returns:
        The registered relax function.

    Raises:
        ValueError: If the name is not a known policy.
    """
    ensure_policies_loaded()
    try:
        return _RELAX_POLICIES[name]
    except KeyError:
        known = ", ".join(sorted(_RELAX_POLICIES)) or "(none registered)"
        raise ValueError(f"Unknown validation policy '{name}'. Known policies: {known}.") from None


def known_relax_policies() -> tuple[str, ...]:
    """Return the registered policy names, sorted (external policies included)."""
    ensure_policies_loaded()
    return tuple(sorted(_RELAX_POLICIES))
