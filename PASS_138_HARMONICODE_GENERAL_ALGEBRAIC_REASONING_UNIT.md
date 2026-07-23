# Pass 138 — HARMONICODE General Algebraic Reasoning Unit
## “The Looking Glass of Logic”

Pass 138 provides a callable, deterministic, proof-carrying algebra API for agentic HHS clients.

## Execution contract

`request -> typed ingress -> exact rational environment -> constraint admission -> goal execution -> proof witnesses -> Looking Glass reverse trace -> authority-bounded conclusion -> receipt validation`

### Looking Glass invariant

A conclusion is admissible only when its forward proof path can be reflected exactly back to the same ingress root:

`Forward(premises, rules) = conclusion`

`Reverse(conclusion, reversed rules) = same premises`

The reflection is lineage and validation, not an assumption that every algebraic operator is globally invertible.

## Authority rules

- Failed constraints block goal execution.
- Failed goals return `GOAL_NOT_PROVED`; they are never promoted.
- Exact rationals only; floats and booleans are rejected.
- Noninteger powers require a separate typed operator contract.
- Every gate has a SHA-256 witness root.
- Every result has a deterministic receipt root.

## API

Python:

```python
from hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 import execute_request
receipt = execute_request(request)
```

CLI:

```bash
python -m hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 request.json --output receipt.json
```
