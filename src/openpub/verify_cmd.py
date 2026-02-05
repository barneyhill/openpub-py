import importlib.util
import json
import sys
from pathlib import Path

import click

from openpub.comparison import compare_values
from openpub.registry import clear_registry, get_registry


def _discover_modules(directory: Path) -> list[Path]:
    """Find all .py files in the directory, excluding _-prefixed files."""
    return sorted(
        p for p in directory.glob("*.py")
        if not p.name.startswith("_")
    )


def _import_module_from_path(path: Path) -> None:
    """Import a Python module from a file path, triggering @claim registrations."""
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def run_verify(claims_path: str, directory: str) -> int:
    """Run verification of claims. Returns exit code (0 = success, 1 = failures)."""
    claims_file = Path(claims_path)
    if not claims_file.exists():
        click.secho(f"Error: claims file not found: {claims_path}", fg="red")
        return 1

    claims = json.loads(claims_file.read_text())
    claims_with_expected = {c["claim_id"]: c for c in claims if "expected" in c}

    # Clear registry and discover modules
    clear_registry()
    cwd = Path(directory)
    for py_file in _discover_modules(cwd):
        try:
            _import_module_from_path(py_file)
        except Exception as e:
            click.secho(f"Warning: failed to import {py_file.name}: {e}", fg="yellow")

    registry = get_registry()

    verified = []
    failed = []
    errors = []
    open_claims = []

    for claim_id, claim_data in sorted(claims_with_expected.items(), key=lambda x: _sort_key(x[0])):
        expected = claim_data["expected"]

        if claim_id not in registry:
            open_claims.append(claim_id)
            continue

        fn = registry[claim_id]
        try:
            result = fn()
        except Exception as e:
            errors.append((claim_id, str(e)))
            continue

        if not isinstance(result, dict):
            errors.append((claim_id, f"returned {type(result).__name__}, expected dict"))
            continue

        failures = compare_values(expected, result)
        if failures:
            failed.append((claim_id, failures))
        else:
            verified.append(claim_id)

    # Report results
    _print_results(verified, failed, errors, open_claims, len(claims_with_expected))

    if failed or errors:
        return 1
    return 0


def _sort_key(claim_id: str) -> tuple[str, int]:
    """Sort claim IDs like C1, C2, ..., C10 numerically."""
    prefix = ""
    num = 0
    for i, ch in enumerate(claim_id):
        if ch.isdigit():
            prefix = claim_id[:i]
            num = int(claim_id[i:])
            break
    return (prefix, num)


def _print_results(
    verified: list[str],
    failed: list[tuple[str, list[str]]],
    errors: list[tuple[str, str]],
    open_claims: list[str],
    total: int,
) -> None:
    """Print colored verification results."""
    click.echo()

    if verified:
        click.secho(f"  VERIFIED ({len(verified)})", fg="green", bold=True)
        for cid in verified:
            click.secho(f"    {cid}", fg="green")

    if failed:
        click.echo()
        click.secho(f"  FAILED ({len(failed)})", fg="red", bold=True)
        for cid, failures in failed:
            click.secho(f"    {cid}:", fg="red")
            for f in failures:
                click.secho(f"      {f}", fg="red")

    if errors:
        click.echo()
        click.secho(f"  ERRORS ({len(errors)})", fg="yellow", bold=True)
        for cid, msg in errors:
            click.secho(f"    {cid}: {msg}", fg="yellow")

    if open_claims:
        click.echo()
        click.secho(f"  OPEN ({len(open_claims)})", fg="cyan", bold=True)
        for cid in open_claims:
            click.secho(f"    {cid}", fg="cyan")

    click.echo()
    click.echo(
        f"  {len(verified)}/{total} verified, "
        f"{len(failed)} failed, "
        f"{len(errors)} errors, "
        f"{len(open_claims)} open"
    )
    click.echo()
