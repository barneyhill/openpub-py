import pytest

from openpub.registry import clear_registry


@pytest.fixture(autouse=True)
def _clear_registry():
    """Clear the claim registry before each test."""
    clear_registry()
    yield
    clear_registry()
