from collections.abc import Callable
from typing import Any

_registry: dict[str, Callable[[], Any]] = {}


def claim(claim_id: str) -> Callable:
    """Decorator that registers a function as the verifier for a claim ID.

    Usage:
        @claim("C5")
        def verify_c5():
            return {"n_with_recurrent_variant": 89, ...}
    """
    def decorator(fn: Callable[[], Any]) -> Callable[[], Any]:
        if claim_id in _registry:
            raise ValueError(
                f"Duplicate claim ID {claim_id!r}: "
                f"already registered to {_registry[claim_id].__name__!r}"
            )
        _registry[claim_id] = fn
        return fn
    return decorator


def get_registry() -> dict[str, Callable[[], Any]]:
    """Return a copy of the current claim registry."""
    return dict(_registry)


def clear_registry() -> None:
    """Clear all registered claims. Used for testing."""
    _registry.clear()
