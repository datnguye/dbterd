"""Registry of named validation-relaxation policies.

Each policy is a function that loosens dbt-artifacts-parser Pydantic validation in a
specific way (e.g. ignore unknown fields, widen unknown enum values). Users opt in by
listing policy names in the ``validation`` config; only listed policies run, so an empty
list means strict validation.
"""

from collections.abc import Callable


# name -> relax function. Populated by @register_relax_policy.
_RELAX_POLICIES: dict[str, Callable[[object], None]] = {}

RelaxPolicy = Callable[[object], None]


def register_relax_policy(name: str) -> Callable[[RelaxPolicy], RelaxPolicy]:
    """Register a relaxation function under a policy name.

    Args:
        name: The policy name users reference in the ``validation`` config.

    Returns:
        Decorator that records the function and returns it unchanged.

    Example:
        @register_relax_policy("relax_extra_fields")
        def relax_pydantic_models(artifact_module): ...
    """

    def decorator(func: RelaxPolicy) -> RelaxPolicy:
        _RELAX_POLICIES[name] = func
        return func

    return decorator


def get_relax_policy(name: str) -> RelaxPolicy:
    """Resolve a policy name to its relax function.

    Args:
        name: The configured policy name.

    Returns:
        The registered relax function.

    Raises:
        ValueError: If the name is not a known policy.
    """
    try:
        return _RELAX_POLICIES[name]
    except KeyError:
        known = ", ".join(sorted(_RELAX_POLICIES)) or "(none registered)"
        raise ValueError(f"Unknown validation policy '{name}'. Known policies: {known}.") from None


def known_relax_policies() -> tuple[str, ...]:
    """Return the registered policy names, sorted."""
    return tuple(sorted(_RELAX_POLICIES))
