import json
from pathlib import Path

from openpub.registry import clear_registry
from openpub.verify_cmd import run_verify


def test_verify_all_pass(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    analysis = tmp_path / "analysis.py"
    analysis.write_text(
        'from openpub import claim\n\n'
        '@claim("C1")\n'
        'def verify_c1():\n'
        '    return {"n": 10}\n'
    )

    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    assert exit_code == 0


def test_verify_failure(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    analysis = tmp_path / "analysis.py"
    analysis.write_text(
        'from openpub import claim\n\n'
        '@claim("C1")\n'
        'def verify_c1():\n'
        '    return {"n": 99}\n'
    )

    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    assert exit_code == 1


def test_verify_error_exception(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    analysis = tmp_path / "analysis.py"
    analysis.write_text(
        'from openpub import claim\n\n'
        '@claim("C1")\n'
        'def verify_c1():\n'
        '    raise RuntimeError("oops")\n'
    )

    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    assert exit_code == 1


def test_verify_open_claims(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    # No analysis.py — all claims are open
    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    # Open claims don't cause failure
    assert exit_code == 0


def test_verify_missing_claims_file(tmp_path):
    clear_registry()
    exit_code = run_verify(str(tmp_path / "nonexistent.json"), str(tmp_path))
    assert exit_code == 1


def test_verify_tolerance(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"pct": {"value": 77.4, "tolerance": 0.1}},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    analysis = tmp_path / "analysis.py"
    analysis.write_text(
        'from openpub import claim\n\n'
        '@claim("C1")\n'
        'def verify_c1():\n'
        '    return {"pct": 77.35}\n'
    )

    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    assert exit_code == 0


def test_verify_skips_underscore_files(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    # This _-prefixed file should be skipped
    hidden = tmp_path / "_hidden.py"
    hidden.write_text(
        'from openpub import claim\n\n'
        '@claim("C1")\n'
        'def verify_c1():\n'
        '    return {"n": 10}\n'
    )

    clear_registry()
    exit_code = run_verify(str(claims_file), str(tmp_path))
    # C1 should be open since _hidden.py is skipped
    assert exit_code == 0
