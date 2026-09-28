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


## Experiment benchmark import-path repair — 2026-09-27

Exact-head validation on `ad59bdde4622571ef26bab2c19535503d751e2cd` established:

- dependency-scoped pytest: **16 passed**;
- Hash216 Repository Dependency Index `36359712883`: **success**;
- dedicated NumPy A/B workflow `36359712902`: failed only at benchmark launch;
- HHS Consensus Gate `36359712841`: failed on the inherited pre-#622
  direct-path acceptance-gate import and is not attributable to the experiment.

Dedicated experiment failure:

```text
python benchmarks/pass220/pass220_numpy_four_phase_ab_v1.py
ModuleNotFoundError: No module named 'hhs_runtime'
```

Root cause: executing a nested benchmark by filesystem path makes the benchmark
directory, rather than repository root, the import anchor.

Repair:
- invoke the benchmark as
  `python -m benchmarks.pass220.pass220_numpy_four_phase_ab_v1`;
- preserve the measured artifact arguments unchanged;
- add a regression that requires package-module invocation and forbids the
  direct-path form.

No experiment semantics, tensor payload, U9 constraints, NumPy ingress/egress,
VM81, Hash72, Hash216, or temporal authority changed.

Next action:
1. inspect the new exact-head dedicated NumPy A/B workflow once;
2. if green, freeze the measured A/B result;
3. treat Consensus as inherited mainline repair debt until #622 lands;
4. repair-forward any actual mainline conflict before merge.


## Measured A/B result frozen — 2026-09-28

Dedicated workflow `36363194046` completed successfully on
`22e83e794d7506dbaf86c0baef98819e65ad11c3`.

Validation:
- dependency-scoped pytest: PASS;
- benchmark artifact upload: PASS;
- semantic identity: true;
- supplied U9 circuit tensor: `U9^9 = I`, nine distinct pre-closure
  positional states, exact inverse recovery, and byte-identical payload
  retention;
- Hash216 dependency index `36363193969`: PASS.

Measured median latency over 15 samples per channel:

| channel | dense A | scalar-offset B | B speedup |
| --- | ---: | ---: | ---: |
| xy | 573355 ns | 132438 ns | 4.3292x |
| yx | 563336 ns | 131546 ns | 4.2824x |
| zw | 561953 ns | 131897 ns | 4.2605x |
| wz | 562223 ns | 132378 ns | 4.2471x |

Logical control storage:
- dense A: 2916 matrix cells;
- scalar-offset B: 324 index references + 36 scalar controls = 360 units;
- exact dense/B control ratio: `81/10`.

Candidate decision:
`SCALAR_SYMBOL_PERMUTATION_CONTROL_PLUS_OFFSET_VECTORIZATION` is selected
for the NumPy1 internal representation candidate.  This is a representation
selection, not an authority expansion.  External ingress/egress remains
unchanged and timing remains explicitly noncanonical.

Frozen evidence:
`evidence/pass220/PASS_220_NUMPY1_FOUR_PHASE_AB_MEASURED_RESULT_20260928.json`

Artifact:
- Actions artifact id: `10946785500`
- uploaded zip SHA-256:
  `adf76ccf4d6112f61e5f5f5c85429a4ef1d568a51b885a3c00e564dca44dad87`

HHS Consensus on this stale experiment base remains inherited repair debt:
PR #622 is still open and contains the package-invocation/import-root repair.
Do not weaken the experiment or duplicate that repair here.

Next workstream:
- continue native-library metadata/constructor import and HARMONICODE
  interpreter integration using the selected scalar-offset internal candidate;
- repair-forward actual mainline conflicts when #622/#618 land.


## Cross-layer information-preserving priority default — 2026-09-28

The NumPy1 scalar-offset result is extended into a cross-layer promotion gate.

Primary rule:

```text
INFORMATION PRESERVATION FIRST
+ PERFORMANCE SUPPORT SECOND
= PRIORITY DEFAULT PROMOTION
```

The complete translated unit is now the tagged tuple:

```text
(value, phase, rotation, original_position)
```

For all ordered channels `xy/yx/zw/wz`, dense Arm A and compact Arm B must
preserve the entire tuple and exact inverse recovery.

Mandatory downstream gates:
- exact 5184-character serialization equality and inverse;
- RNA phase-lock state identity;
- ordered xy/yx/zw/wz Digital-DNA binding identity;
- Pass 115 qudit serialization root, topology, coordinate-bijection, and exact
  value/phase/rotation reconstruction;
- supplied U9 circuit tensor closure and provenance;
- Pass 219 HNAN invariant receipt;
- HNAN ordered Lo Shu receipt;
- terminal `xy+epsilon`;
- bare-`xy`, epsilon-elision, ordered-product commutation, and host-scalar
  epsilon substitution remain forbidden.

New files:
- `hhs_runtime/hhs_pass220_priority_offset_information_translation_v1.py`
- `tests/pass220/test_hhs_pass220_priority_offset_information_translation_v1.py`
- `benchmarks/pass220/pass220_priority_offset_information_translation_v1.py`
- `docs/pass220/PASS_220_PRIORITY_OFFSET_INFORMATION_TRANSLATION_V1.md`

The existing frozen NumPy timing evidence is used only as supporting promotion
evidence. It is explicitly outside Lane 5 and cannot override an information
gate failure.

Promotion semantics:
- information PASS + performance PASS -> `PROMOTE_PRIORITY_DEFAULT`;
- information PASS + performance pending -> dense remains selected while compact
  remains an information-valid candidate;
- any information loss -> `FALL_BACK_TO_DENSE_REFERENCE`.

No VM81 mutation, Hash72 mint, Hash216 persistence, HNAN bypass, or Lane 5
authority is introduced.

Next action:
1. inspect exact-head PR #624 validation once;
2. repair only attributable cross-layer failures;
3. freeze the information-preservation receipt and cross-layer host timing;
4. extend the same promotion gate to native Lane 5 hydration and I048
   constructor/runtime-adapter execution when those branches reconcile.


## Explicit HNAN zero/center identity binding — 2026-09-28

The cross-layer promotion gate now preserves the already-defined explicit HNAN
identity:

```text
0=∅=HNAN=x+y-z-w+xy+yx-zw-wz
```

This is not a replacement for the inherited global denominator closure:

```text
0=∅=AB/P⁴∅=HNAN
```

Both constraint surfaces are mandatory and retained independently.

The information gate now proves:
- the exact combined zero/EmptySet/HNAN/center source string;
- its HNAN-side center equals the existing
  `HNAN_CENTER_EXPRESSION = x+y-z-w+xy+yx-zw-wz`;
- the existing `0=∅=AB/P⁴∅=HNAN` source remains unchanged;
- the residual terminal `xy+epsilon` remains required;
- bare `xy`, epsilon elision, ordered-product commutation, and host-scalar
  substitution remain forbidden.

Therefore compact translation is rejected if it preserves a projected value but
loses either HNAN equality surface or the typed residual information.


## Wolfram HNAN zero-center formalization + whitepaper proof — 2026-09-28

Connected Wolfram Language evaluation formalized the explicit typed source:

```text
0=∅=HNAN=x+y-z-w+xy+yx-zw-wz
```

using inert list ASTs, with the inherited closure

```text
0=∅=AB/P⁴∅=HNAN
```

and residual terminal

```text
xy+epsilon
```

retained as independent witnesses.

Result: **20/20 PASS**.

Key proof obligations:
- exact eight-term center order;
- `xy != yx`, `zw != wz`;
- swapping `xy/yx` changes the center signature;
- structural round-trip of both HNAN closure surfaces;
- removing the center is non-injective over distinct ordered HNAN states;
- removing epsilon is non-injective over distinct residual states;
- the two closure surfaces remain structurally distinct.

Added:
- `evidence/pass220/hnan_zero_center_information_wolfram_20260928_v1.wl`
- `evidence/pass220/hnan_zero_center_information_wolfram_20260928_v1.output.json`
- `docs/whitepapers/HHS_HNAN_ZERO_CENTER_INFORMATION_PRESERVATION_THEOREM_V1.md`

Updated:
- HNAN/Jordan global theorem whitepaper;
- Lane 5 whitepaper index;
- Pass 220 priority-offset information-translation contract;
- dependency-scoped regression tests.

The proof establishes why the string is necessary for translation: deleting the
center makes the HNAN projection many-to-one and therefore destroys unique
reconstruction. Speed cannot override this information-preservation failure.


## Literal firing-pattern provenance binding — 2026-09-28

Clarification frozen into repository evidence: the radial-engine firing pattern
is not being used as an analogy or as a source for a new design. The exact
engineering firing logic is already the phase-engine constructor.

Existing exact schedule:

```text
sigma_n = 8 + 16 n (mod 72)
8 -> 24 -> 40 -> 56 -> 72 -> 16 -> 32 -> 48 -> 64 -> 8
```

Existing proof:
- I025 connected Wolfram: 25/25 PASS;
- 72-position shift-by-16 operator;
- eight disjoint 9-state cycles;
- exact `U72^9 = I`.

Pass 219 Lane 5 consumes the same constructor through
`lane5_genesis_orientation_u9_qe_bridge.py` and
`lane5_feynman_discrete_orbit_bridge.py`.

Added composition receipt:
`evidence/pass220/phase_engine_firing_hnan_composition_20260928_v1.json`.

Regression now fails if the firing orbit, 8x9 cycle decomposition, Pass 219 U9
permutation binding, or HNAN center source drifts.

No second phase engine or metaphor-derived replacement geometry was introduced.
