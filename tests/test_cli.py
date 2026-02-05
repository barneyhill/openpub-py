import json

from click.testing import CliRunner

from openpub.cli import cli
from openpub.registry import clear_registry


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "openpub" in result.output


def test_init_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--help"])
    assert result.exit_code == 0
    assert "CLAIMS_JSON" in result.output


def test_verify_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "--help"])
    assert result.exit_code == 0
    assert "--claims" in result.output


def test_init_e2e(tmp_path):
    claims = [
        {"claim_id": "C1", "claim": "Test", "expected": {"n": 10}},
    ]
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps(claims))

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(cli, ["init", str(claims_file), "-o", str(output_dir)])
    assert result.exit_code == 0
    assert "Scaffolded" in result.output
    assert (output_dir / "analysis.py").exists()


def test_verify_e2e(tmp_path):
    claims = [
        {"claim_id": "C1", "claim": "Test", "expected": {"n": 10}},
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
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "--claims", str(claims_file), "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "VERIFIED" in result.output
