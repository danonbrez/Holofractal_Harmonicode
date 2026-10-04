# Pass 220 I075 — Native Rectangular Tensor-Power Hydration Restart

Date: 2026-10-04

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `45c1dfa8378541fa141de6d19f347cb88cb37d2c`
- Base state: merged Pass 220 I074
- Branch: `pass220/i075-native-rectangular-tensor-power-hydration-20261004`
- Merge target: `main`
- Status: implemented restartable checkpoint; branch CI pending

## Objective

Lower the two I074 held rectangular MatrixPower source nodes into typed native
HARMONICODE tensor-power AST records without assigning host MatrixPower,
ordinary scalar, or numeric exponent semantics.

## Implemented surfaces

### Runtime

`hhs_runtime/hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1.py`

Implements:

- `NativeRectangularTensorPower` typed records;
- exact 4x2 source bases `M_WZ` and `M_XY`;
- exact exponent tokens `x^2` and `x^4`;
- exact source node identities;
- host-evaluation and numeric-exponent-evaluation flags fixed false;
- 16 source-cell occurrence witnesses over a six-expression dictionary;
- I074 parent binding;
- Hash216 PREVIOUS/CHANGE/RECEIPT;
- exact I065 hydration/recompression;
- compact plane-root persistence only.

### Tests

`tests/pass220/test_hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1.py`

Covers typed-node identity, 4x2 shape, source reconstruction, occurrence
provenance, Hash216 hydration, authority non-widening, negative mutation, and
runtime self-test.

### Wolfram

`formal/wolfram/pass220_i075_native_rectangular_tensor_power_hydration_v1.wl`

Connected Wolfram kernel execution:

```text
status = PASS
checks = 24 / 24
failed = {}
node count = 2
shapes = 4x2, 4x2
cell occurrences = 16
unique symbolic cells = 6
host MatrixPower evaluations = 0
numeric exponent evaluations = 0
Hash216 width = 216
full attached components = 15552
```

The first preflight attempt exposed only a Wolfram association-access syntax
mistake in two checks; it was corrected before evidence was frozen. No native
tensor semantics changed.

Frozen evidence:

- `evidence/pass220/i075_native_rectangular_tensor_power_hydration_wolfram_20261004_v1.output.json`
- `evidence/pass220/i075_native_rectangular_tensor_power_hydration_wolfram_20261004_v1.receipt.json`

### Lean 4

`formal/lean/HHS/Pass220/NativeRectangularTensorPowerHydration.lean`

Imports `HHS.Pass220.FullTensorHNANClosureHydration` and proves:

- exactly two native nodes;
- exact 4x2 shapes;
- exact native operator tags;
- exact exponent tokens;
- exact source-node identities;
- host and numeric exponent evaluation remain false;
- `72*72=5184`;
- `3*5184=15552`;
- inherited I074 hydration geometry;
- authority and compact-persistence boundaries.

The root import is inserted in the top-level import header of
`formal/lean/HHS.lean`.

## Frozen structural census

```text
native tensor-power nodes      = 2
rectangular shapes             = 4x2, 4x2
source cell occurrences        = 16
unique symbolic cell roots     = 6
source occurrence witnesses    = 16
host MatrixPower evaluations   = 0
numeric exponent evaluations   = 0
Hash216 width                  = 216
hydrated attached components   = 15552
expanded geometry persisted    = false
```

## Authority boundary

- candidate-only;
- no host MatrixPower authority;
- no rectangular host MatrixPower authority;
- no numeric exponent evaluation authority;
- no projection substitution;
- no floating-point authority;
- no VM81 mutation authority;
- no canonical Hash72/Hash216 commit authority;
- no canonical persistence authority;
- no external-egress authority.

## Validation remaining

Run dependency-scoped branch CI:

1. Python compile;
2. I075 + I074 dependency-scoped tests;
3. I075 runtime self-test;
4. inherited source-bundle blob identities;
5. typed native-node descriptor checks;
6. frozen Wolfram evidence checks;
7. Lean theorem-surface check;
8. Lean build, kernel check, leanchecker, and axiom audit.

Repair only I075 dependency-scoped defects. Do not reopen completed historical
passes.

## Next action

Open the I075 PR against main. Once the dependency-scoped workflow is green,
merge, verify exact main, and repair-forward any post-merge issue without
reopening frozen evidence.
