# Python API Manual

## General Algebraic Reasoning Unit

```python
from hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 import execute_request

receipt = execute_request(request)
```

The request carries exact assignments, equality constraints, and goals. The result must be interpreted through its conclusion and witness records.

## Architect

```python
from hhs_runtime.harmonicode_architect_ouroboros_v1 import Architect

architect = Architect()
receipt = architect.execute(request)
validation = architect.validate_receipt(receipt)
```

The Architect may propose candidates but may commit only evidence-backed improvements.

## Holographic recovery

```python
from hhs_runtime.holographic_entanglement_recovery_v1 import HolographicRecovery

runtime = HolographicRecovery()
encoding = runtime.encode(request)
impact = runtime.analyze_impact(encoding, ["source"])
recovery = runtime.recover(encoding)
```

Recovery is byte-exact within the declared redundancy bound. Metadata resemblance alone is insufficient.

## Receipt validation rule

Always validate a receipt through the authoritative validator associated with its schema. Do not treat the presence of a `status` string as sufficient evidence.

## Authority rule

API clients may submit proposals and consume evidence. They may not rewrite receipt roots, proof classifications, release authority, or ancestry fields and then claim the modified object remains valid.
