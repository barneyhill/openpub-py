from typing import Any


def compare_values(expected: Any, actual: Any, path: str = "") -> list[str]:
    """Compare expected and actual values, returning a list of failure messages.

    Handles:
    - {"value": X, "tolerance": Y} dicts -> tolerance-based numeric comparison
    - Plain int -> exact match (type-strict)
    - Plain float -> near-exact (relative epsilon 1e-9)
    - str -> exact match
    - Nested dict -> recursive comparison
    - Missing keys -> failure; extra keys -> informational, not failure
    """
    failures = []

    if isinstance(expected, dict) and "value" in expected and "tolerance" in expected:
        # Tolerance-based comparison
        if not isinstance(actual, (int, float)):
            failures.append(f"{path}: expected numeric value, got {type(actual).__name__}")
            return failures
        exp_val = expected["value"]
        tol = expected["tolerance"]
        if abs(actual - exp_val) > tol:
            failures.append(
                f"{path}: {actual} != {exp_val} (tolerance {tol}, diff {abs(actual - exp_val):.6g})"
            )
    elif isinstance(expected, dict):
        # Nested dict -> recursive comparison
        if not isinstance(actual, dict):
            failures.append(f"{path}: expected dict, got {type(actual).__name__}")
            return failures
        for key in expected:
            child_path = f"{path}.{key}" if path else key
            if key not in actual:
                failures.append(f"{child_path}: missing key")
            else:
                failures.extend(compare_values(expected[key], actual[key], child_path))
    elif isinstance(expected, int) and not isinstance(expected, bool):
        # Exact integer match (type-strict)
        if not isinstance(actual, int) or isinstance(actual, bool):
            failures.append(f"{path}: expected int, got {type(actual).__name__} ({actual!r})")
        elif actual != expected:
            failures.append(f"{path}: {actual} != {expected}")
    elif isinstance(expected, float):
        # Near-exact float match
        if not isinstance(actual, (int, float)):
            failures.append(f"{path}: expected numeric, got {type(actual).__name__}")
        elif expected == 0.0:
            if abs(actual) > 1e-9:
                failures.append(f"{path}: {actual} != {expected}")
        elif abs(actual - expected) / max(abs(expected), 1e-15) > 1e-9:
            failures.append(f"{path}: {actual} != {expected}")
    elif isinstance(expected, str):
        if actual != expected:
            failures.append(f"{path}: {actual!r} != {expected!r}")
    else:
        if actual != expected:
            failures.append(f"{path}: {actual!r} != {expected!r}")

    return failures
