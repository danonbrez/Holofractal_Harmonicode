# Pass 220 NumPy1 Four-Phase A/B Experiment — 2026-09-27

Status: IMPLEMENTED / VALIDATION PENDING

## Restart state

- repository: danonbrez/Holofractal_Harmonicode
- base commit: 80cac0031a0d3377627a7dcfb81be1f8c0b2ae69
- branch: experiment/pass220-numpy1-four-phase-ab-20260927
- merge target: main
- source NumPy1 module: hhs_runtime/hhs_pass220_numpy_harmonicode_array_v1.py
- experiment module: hhs_runtime/hhs_pass220_numpy_four_phase_ab_v1.py

## Objective

Compare two candidate representations for the existing NumPy1 fixed-width 5184
carrier without changing the external NumPy compatibility membrane:

A. dense nine-position substitution tensors;
B. scalar-symbol permutation control plus offset vectorization.

Both arms consume the same 81 normalization offsets and the same Pass 219 U9
address-permutation convention.  The scalar symbol controls permutation; it
does not scalarize or replace the payload tensor.

Four ordered channels are retained:

- Aa -> xy
- Ba -> yx
- Ab -> zw
- Bb -> wz

The reciprocal permutation factors are (1,-1) and (2,-2) modulo the nine-state
U9 orbit.  Zero offsets remain typed positional spacers and are never trimmed.

## Acceptance

The experiment requires:

1. exact IEEE binary64 ingress/recovery identity;
2. exact 5184-character source and transformed carrier widths;
3. dense substitution and scalar-offset-vector arms produce identical offsets
   for all four ordered channels;
4. inverse permutation restores the original 81 offsets and 5184 carrier;
5. zero-spacer cardinality is retained through every channel;
6. existing Pass 220 I033 palindromic constructor validation remains green;
7. candidate B has lower declared logical control storage than dense A;
8. no VM81 mutation, Hash72 mint, or Hash216 persistence authority is added.

Declared control storage for one four-channel 81-cell object:

- dense A: 2916 matrix cells;
- vector B: 324 index references + 36 scalar-symbol controls = 360 units;
- exact dense/vector ratio: 81/10.

The storage comparison is representation-level.  Runtime timing is separately
measured and explicitly noncanonical.

## Validation

Dependency-scoped validation is wired in:

```text
pytest -q tests/pass220/test_hhs_pass220_numpy_four_phase_ab_v1.py
python benchmarks/pass220/pass220_numpy_four_phase_ab_v1.py --output artifacts/pass220/numpy1_four_phase_ab.json --repeats 15
```

The dedicated pull-request workflow uploads the measured A/B artifact.

## Merge/rebase policy

The user authorized continuing this experiment while #622/#618 repair closure
continues.  If main changes before merge, preserve this branch and repair
forward only actual merge conflicts; do not discard the experiment or weaken
the existing ingress/egress, RNA, VM81, Hash72, Hash216, or temporal gates.

## Next action

1. run the dedicated PR validation;
2. inspect exact failures once and repair forward if needed;
3. use the measured artifact plus exact semantic identity to decide whether the
   scalar-offset representation should be promoted into NumPy1 internals;
4. after promotion/selection, continue native library import metadata mapping
   and the HARMONICODE interpreter workstream.


## Supplied ordered 3×3 tensor extension — 2026-09-27

The experiment now also tests the user-supplied tensor verbatim:

```text
[
  [(x*y), x+y, (y*x)],
  [(x*y)-(z*w), x+y-z-w+(x*y)+(y*x)-(z*w)-(w*z), (w*z)-(y*x)],
  [(w*z), z+w, (z*w)]
]
```

The implementation preserves this as a literal ordered symbolic object.  A
lexical notation projection maps only the four explicit product spellings:

```text
(x*y) -> xy
(y*x) -> yx
(z*w) -> zw
(w*z) -> wz
```

No algebraic simplification, commutation, factorization, or expression-term
reordering is authorized.  The projected tensor must equal the existing
repository-authoritative `EIGENVECTOR0_TENSOR` exactly.

The tensor is then exercised under every one of the nine scalar-symbol controls
and all four ordered Aa/Ba/Ab/Bb channels: 9 × 4 = 36 cases.  For every case:

1. dense substitution-tensor arm A must equal scalar/permutation arm B;
2. inverse permutation must recover all nine original ordered expressions;
3. the expression multiset must be preserved exactly;
4. `xy != yx` and `wz != zw` remain explicit;
5. the center remains exactly `x+y-z-w+xy+yx-zw-wz`.

The tensor witness is now part of NumPy scalar experiment acceptance and is also
recorded in the measured benchmark artifact.

Next action:
- inspect the new exact-head PR #624 validation once;
- repair only attributable failures;
- preserve this checkpoint if main advances and repair forward merge conflicts.


## Scope correction — supplied circuit tensor under U9 constraints

The prior extension incorrectly made a notation projection to the existing
`EIGENVECTOR0_TENSOR` the primary test.  That is no longer the acceptance
surface.

The supplied circuit tensor is now consumed verbatim as the nine-cell U9 state:

```text
[
  [(x*y), x+y, (y*x)],
  [(x*y)-(z*w), x+y-z-w+(x*y)+(y*x)-(z*w)-(w*z), (w*z)-(y*x)],
  [(w*z), z+w, (z*w)]
]
```

Repository U9 authority is applied directly:

```text
U9 = macrocycle_permutation() = shift-by-one on 9 addresses
U9^9 = I
```

Required constraints:
1. one U9 step is not identity;
2. powers U9^0..U9^8 produce nine distinct address states;
3. U9^9 returns the exact original literal circuit tensor;
4. direct U9^k and iterative U9 application are identical for every power;
5. dense substitution-matrix U9 and direct permutation-vector U9 are identical;
6. inverse U9 power recovers the exact original tensor for every state;
7. every state contains exactly the same nine literal circuit cells;
8. no notation projection, simplification, commutation, factorization, or
   within-cell term reordering is used.

This U9 witness is now mandatory for overall NumPy experiment acceptance.
The earlier lexical comparison is no longer the governing tensor test.
