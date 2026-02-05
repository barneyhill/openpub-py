from openpub.comparison import compare_values


def test_exact_int_match():
    assert compare_values(42, 42) == []


def test_exact_int_mismatch():
    failures = compare_values(42, 43)
    assert len(failures) == 1
    assert "43 != 42" in failures[0]


def test_int_type_strict():
    failures = compare_values(42, 42.0)
    assert len(failures) == 1


def test_exact_float_match():
    assert compare_values(3.14, 3.14) == []


def test_float_near_match():
    assert compare_values(1.0, 1.0 + 1e-12) == []


def test_float_mismatch():
    failures = compare_values(3.14, 3.15)
    assert len(failures) == 1


def test_string_match():
    assert compare_values("hello", "hello") == []


def test_string_mismatch():
    failures = compare_values("hello", "world")
    assert len(failures) == 1


def test_tolerance_match():
    expected = {"value": 77.4, "tolerance": 0.1}
    assert compare_values(expected, 77.35) == []


def test_tolerance_mismatch():
    expected = {"value": 77.4, "tolerance": 0.1}
    failures = compare_values(expected, 78.0)
    assert len(failures) == 1


def test_tolerance_non_numeric():
    expected = {"value": 77.4, "tolerance": 0.1}
    failures = compare_values(expected, "not a number")
    assert len(failures) == 1
    assert "expected numeric" in failures[0]


def test_nested_dict():
    expected = {"a": 1, "b": {"value": 3.0, "tolerance": 0.5}}
    actual = {"a": 1, "b": 3.1}
    assert compare_values(expected, actual) == []


def test_nested_dict_missing_key():
    expected = {"a": 1, "b": 2}
    actual = {"a": 1}
    failures = compare_values(expected, actual)
    assert len(failures) == 1
    assert "missing key" in failures[0]


def test_nested_dict_extra_key_ok():
    expected = {"a": 1}
    actual = {"a": 1, "extra": "stuff"}
    assert compare_values(expected, actual) == []


def test_deeply_nested():
    expected = {"outer": {"inner": {"value": 0.5, "tolerance": 0.01}}}
    actual = {"outer": {"inner": 0.505}}
    assert compare_values(expected, actual) == []


def test_expected_dict_actual_not_dict():
    expected = {"a": 1}
    failures = compare_values(expected, "not a dict")
    assert len(failures) == 1
    assert "expected dict" in failures[0]


def test_float_zero():
    assert compare_values(0.0, 0.0) == []
    failures = compare_values(0.0, 1.0)
    assert len(failures) == 1
