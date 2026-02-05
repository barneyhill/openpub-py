# openpub

A CLI tool for verifying scientific paper claims with code.

openpub scaffolds verification projects from structured claims and runs `@claim`-decorated functions against expected values, reporting which claims pass, fail, or remain open.

## Install

```bash
pip install openpub
```

## Usage

### Scaffold a verification project

```bash
openpub init claims.json -o my-paper/
```

This generates:

- `analysis.py` — stub functions decorated with `@claim` for each verifiable claim
- `claims.json` — copy of the input claims
- `pyproject.toml` and `README.md`

### Write verification logic

Fill in the generated stubs in `analysis.py`:

```python
from openpub import claim

@claim("C1")
def verify_c1():
    """Verify: The dataset contains 150 samples."""
    # Your analysis code here
    n_samples = 150
    return {"n_samples": n_samples}
```

Each function returns a dict of key-value pairs that are compared against the expected values in `claims.json`.

### Run verification

```bash
openpub verify --claims claims.json --dir .
```

Output shows which claims are verified, failed, errored, or still open.

## Comparison rules

Expected values in `claims.json` support:

| Type | Comparison |
|------|-----------|
| `int` | Exact match (type-strict) |
| `float` | Near-exact (relative epsilon 1e-9) |
| `str` | Exact match |
| `{"value": X, "tolerance": Y}` | `abs(actual - X) <= Y` |
| Nested `dict` | Recursive comparison; missing keys fail, extra keys allowed |

## Development

```bash
git clone https://github.com/barneyhill/openpub-py.git
cd openpub-py
uv pip install -e ".[dev]"
pytest
```
