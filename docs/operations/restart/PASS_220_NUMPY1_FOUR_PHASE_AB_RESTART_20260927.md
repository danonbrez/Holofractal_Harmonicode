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


## Corrected supplied circuit tensor under U9 — 2026-09-27

The earlier 3×3 payload was incorrect and is superseded.  The authoritative
experiment payload is the complete user-supplied circuit tensor, stored exactly
at:

`contracts/pass220/PASS_220_NUMPY1_SUPPLIED_U9_CIRCUIT_TENSOR_1_0.harmonicode`

The exact payload is:

```text
(x*y*List(x*((z*179971179971)/(w*1000000)),y*((w*179971179971)/(z*179971)),z*((z*179971179971)/(w*1000001)),w*((w*179971179971)/(z*179971.179971)))^(z^4==x^2*z^2))*(z*w*List(x*((x*179971179971)/(y*1000000)),y*((y*179971179971)/(x*179971)),z*((x*179971179971)/(y*1000001)),w*((y*179971179971)/(x*179971.179971)))^(x^2==x*z))==(MatrixTimes(MatrixTimes(-x,MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),-Pi)),MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),Pi))==MatrixTimes(x^2,MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),Pi*x))==x*y)/(List((179971179971^((z^4==x^2*z^2)+(x^2==x*z))*w*x*(x^2/y)^(x^2==x*z)*y*z*((x*z)/w)^(z^4==x^2*z^2))/10^(6*((z^4==x^2*z^2)+(x^2==x*z))),(1000001^((z^4==x^2*z^2)+(x^2==x*z))*w*x*y*(y^2/x)^(x^2==x*z))*(((w*y)/z)^(z^4==x^2*z^2)*z),(179971^((z^4==x^2*z^2)+(x^2==x*z))*w*x*y*z*((x*z)/y)^(x^2==x*z))*(z^2/w)^(z^4==x^2*z^2),(10^(6*((z^4==x^2*z^2)+(x^2==x*z)))*w*x*y*((w*y)/x)^(x^2==x*z))*((w^2/z)^(z^4==x^2*z^2)*z))==1)
```

This entire expression is one indivisible circuit tensor.  The experiment does
not parse or independently solve any equality-chain segment, List, MatrixTimes,
MatrixPower, exponent, denominator, decimal/scientific constant, or ordered
x/y/z/w product.

U9 acts only on nine tagged positional/provenance slots that each carry this
same exact tensor.  The slot tag is external provenance; it is not inserted into
or substituted into the tensor.

Required U9 constraints:
1. `U9^9 = I`;
2. powers 0..8 yield nine distinct positional states by slot order;
3. the ninth transition returns the exact tagged source state;
4. dense substitution control equals direct permutation-vector control at every
   U9 power;
5. iterative U9 equals direct `U9^k`;
6. inverse U9 recovers the exact source state at every power;
7. every slot retains the circuit tensor byte-for-byte;
8. all four Aa/Ba/Ab/Bb channels cover U9 powers 0..8 across the nine scalar
   controls, giving 36 channel/control cases with exact A/B identity;
9. internal algebra remains opaque: no parsing, simplification, commutation,
   factorization, projection, or term reordering;
10. no VM81 mutation, Hash72 mint, or Hash216 persistence authority is added.

The U9 circuit-tensor witness is mandatory for overall NumPy A/B acceptance and
its payload SHA plus closure results are included in the benchmark artifact.

Next action:
- inspect exact-head PR #624 validation once;
- repair only attributable failures;
- preserve this branch across later mainline repair merges and repair forward
  only real conflicts.
