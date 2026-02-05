import pytest

from openpub import claim
from openpub.registry import clear_registry, get_registry


def test_register_claim():
    @claim("C1")
    def verify_c1():
        return {"x": 1}

    reg = get_registry()
    assert "C1" in reg
    assert reg["C1"] is verify_c1


def test_duplicate_claim_raises():
    @claim("C1")
    def verify_c1():
        return {}

    with pytest.raises(ValueError, match="Duplicate claim ID"):
        @claim("C1")
        def verify_c1_again():
            return {}


def test_decorator_preserves_function():
    @claim("C1")
    def verify_c1():
        return {"answer": 42}

    assert verify_c1() == {"answer": 42}


def test_clear_registry():
    @claim("C1")
    def verify_c1():
        return {}

    assert len(get_registry()) == 1
    clear_registry()
    assert len(get_registry()) == 0


def test_get_registry_returns_copy():
    @claim("C1")
    def verify_c1():
        return {}

    reg = get_registry()
    reg["C99"] = lambda: {}
    assert "C99" not in get_registry()
