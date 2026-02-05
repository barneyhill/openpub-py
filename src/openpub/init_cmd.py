import json
import shutil
from pathlib import Path
from typing import Any


def _make_function_name(claim_id: str) -> str:
    """Convert claim ID like 'C5' to function name like 'verify_c5'."""
    return f"verify_{claim_id.lower()}"


def _format_return_value(expected: dict[str, Any], indent: int = 1) -> str:
    """Format expected values as a Python return dict literal."""
    lines = []
    prefix = "    " * indent
    lines.append("{")
    items = list(expected.items())
    for i, (key, val) in enumerate(items):
        comma = "," if i < len(items) - 1 else ","
        if isinstance(val, dict) and "value" in val and "tolerance" in val:
            # Tolerance value: emit the scalar with a tolerance comment
            lines.append(f'{prefix}    "{key}": {_format_scalar(val["value"])},{comma[:-1]}  # tolerance: {val["tolerance"]}')
        elif isinstance(val, dict):
            # Nested dict
            nested = _format_return_value(val, indent + 1)
            lines.append(f'{prefix}    "{key}": {nested}{comma}')
        else:
            lines.append(f'{prefix}    "{key}": {_format_scalar(val)}{comma}')
    lines.append(f"{prefix}}}")
    return "\n".join(lines)


def _format_scalar(val: Any) -> str:
    """Format a scalar value as a Python literal."""
    if isinstance(val, str):
        return repr(val)
    if isinstance(val, bool):
        return repr(val)
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return repr(val)
    return repr(val)


def generate_analysis_py(claims: list[dict]) -> str:
    """Generate analysis.py content with stub functions for claims with expected values."""
    lines = ['from openpub import claim', '', '']

    claims_with_expected = [c for c in claims if "expected" in c]

    for i, c in enumerate(claims_with_expected):
        claim_id = c["claim_id"]
        fn_name = _make_function_name(claim_id)
        expected = c["expected"]

        lines.append(f'@claim("{claim_id}")')
        lines.append(f'def {fn_name}():')
        lines.append(f'    """Verify: {c["claim"][:80]}"""')

        return_dict = _format_return_value(expected)
        lines.append(f'    return {return_dict}')

        if i < len(claims_with_expected) - 1:
            lines.append('')
            lines.append('')

    lines.append('')
    return "\n".join(lines)


def generate_pyproject_toml() -> str:
    """Generate a minimal pyproject.toml for the scaffolded project."""
    return '''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-paper"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "openpub",
]
'''


def generate_readme(claims: list[dict]) -> str:
    """Generate a README.md for the scaffolded project."""
    total = len(claims)
    with_expected = sum(1 for c in claims if "expected" in c)
    return f"""# Paper Verification

This project uses [openpub](https://pypi.org/project/openpub/) to verify scientific claims.

- **Total claims**: {total}
- **Verifiable claims** (with expected values): {with_expected}

## Quick Start

```bash
# Install dependencies
uv pip install -e .

# Run verification
openpub verify
```

## Files

- `claims.json` — Structured claims extracted from the paper
- `analysis.py` — Verification functions decorated with `@claim`
"""


def run_init(claims_path: str, output_dir: str) -> None:
    """Scaffold a paper verification project from a claims JSON file."""
    claims_file = Path(claims_path)
    if not claims_file.exists():
        raise FileNotFoundError(f"Claims file not found: {claims_path}")

    claims = json.loads(claims_file.read_text())
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # analysis.py
    (out / "analysis.py").write_text(generate_analysis_py(claims))

    # pyproject.toml
    (out / "pyproject.toml").write_text(generate_pyproject_toml())

    # README.md
    (out / "README.md").write_text(generate_readme(claims))

    # claims.json (copy verbatim)
    shutil.copy2(claims_file, out / "claims.json")
