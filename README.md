# openpub

A CLI tool for verifying scientific paper claims with code.

openpub scaffolds verification projects from structured claims and runs `@claim`-decorated functions against expected values, reporting which claims pass, fail, or remain open.

Part of the [open, machine-readable scientific publishing](https://www.biorxiv.org/content/10.64898/2026.01.30.702911v1) workflow. Use [cllm](https://github.com/barneyhill/cllm) to extract structured claims from a manuscript, then use openpub to verify them computationally.

```
manuscript.txt ──► cllm extract ──► claims.json ──► openpub init ──► analysis.py
                                                                          │
                                                    openpub verify ◄──────┘
```

## Install

```bash
pip install openpub
```

## Usage

### 1. Extract claims (via cllm)

```bash
cllm extract manuscript.txt -o claims.json
```

This produces a JSON array of claims, each with a `claim_id`, description, evidence metadata, and optionally an `expected` dict of verifiable values:

```json
[
  {
    "claim_id": "C4",
    "claim": "115 individuals with NDD have heterozygous variants in the critical region",
    "claim_type": "EXPLICIT",
    "source": "we identify heterozygous variants in 115 individuals with NDD",
    "source_type": ["TEXT"],
    "evidence": "Direct count from study cohorts",
    "evidence_type": ["DATA"],
    "expected": {
      "n_individuals_with_variants": 115
    }
  }
]
```

Only claims with an `expected` field are verifiable by openpub.

### 2. Scaffold a verification project

```bash
openpub init claims.json -o my-paper/
```

This generates:

- `analysis.py` — stub functions decorated with `@claim` for each verifiable claim
- `claims.json` — copy of the input claims
- `pyproject.toml` and `README.md`

### 3. Write verification logic

Fill in the generated stubs in `analysis.py`:

```python
from openpub import claim

@claim("C4")
def verify_c4():
    """Verify: 115 individuals with NDD have heterozygous variants."""
    df = load_cohort_data()
    n = len(df[df["has_variant"]])
    return {"n_individuals_with_variants": n}
```

Each function returns a dict of key-value pairs that are compared against the `expected` values in `claims.json`.

### 4. Run verification

```bash
openpub verify --claims claims.json --dir .
```

Output categorises each claim as:

- **VERIFIED** — returned values match expected
- **FAILED** — values don't match
- **ERROR** — function raised an exception
- **OPEN** — no verification function registered yet

Exit code is `0` if no failures or errors, `1` otherwise. Open claims are allowed.

## Comparison rules

Expected values in `claims.json` support:

| Type | Comparison |
|------|-----------|
| `int` | Exact match (type-strict: `42 != 42.0`) |
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
