import json
from pathlib import Path

from openpub.init_cmd import generate_analysis_py, run_init


def test_generate_analysis_py_basic():
    claims = [
        {"claim_id": "C1", "claim": "Some claim without expected"},
        {
            "claim_id": "C2",
            "claim": "A verifiable claim",
            "expected": {"count": 42, "ratio": {"value": 0.5, "tolerance": 0.01}},
        },
    ]
    code = generate_analysis_py(claims)
    assert "from openpub import claim" in code
    assert '@claim("C2")' in code
    assert "def verify_c2():" in code
    assert '"count": 42' in code
    assert "# tolerance: 0.01" in code
    # C1 has no expected, should not appear
    assert "C1" not in code


def test_generate_analysis_py_no_expected():
    claims = [{"claim_id": "C1", "claim": "No expected values"}]
    code = generate_analysis_py(claims)
    assert "from openpub import claim" in code
    assert "def " not in code or "verify" not in code


def test_run_init(tmp_path):
    claims = [
        {
            "claim_id": "C1",
            "claim": "Test claim",
            "expected": {"n": 10},
        }
    ]
    claims_file = tmp_path / "input" / "claims.json"
    claims_file.parent.mkdir()
    claims_file.write_text(json.dumps(claims))

    output_dir = tmp_path / "output"
    run_init(str(claims_file), str(output_dir))

    assert (output_dir / "analysis.py").exists()
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "README.md").exists()
    assert (output_dir / "claims.json").exists()

    # Verify claims.json was copied
    copied = json.loads((output_dir / "claims.json").read_text())
    assert copied == claims

    # Verify analysis.py has the function
    analysis_code = (output_dir / "analysis.py").read_text()
    assert '@claim("C1")' in analysis_code
    assert "def verify_c1" in analysis_code

    # Verify README has counts
    readme = (output_dir / "README.md").read_text()
    assert "1" in readme


def test_run_init_missing_file(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        run_init(str(tmp_path / "nonexistent.json"), str(tmp_path / "out"))
