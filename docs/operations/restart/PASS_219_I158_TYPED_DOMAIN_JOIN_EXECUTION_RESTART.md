# Pass 219 I158 — Typed-Domain Join Execution Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 2d9efd5e2960c42b7c762c95389b9688cfcb8433`
- Branch: `agent/pass219-i158-typed-domain-join-execution`
- Merge target: `main`
- Implementation head before validation: `d9d1d60e0afe638e8565d123e14b7b81153c1522`

## Purpose

I158 executes every I157 typed join whose semantics are already registered and
independently verifiable.

It closes both modular-pivot joins through exact rational-to-modular projection
witnesses and preserves the three still-unregistered boundary/root joins as
explicit fail-closed blockers.

## Implemented files

- `hhs_runtime/pass219/typed_domain_join_executor.py`
- `tests/pass219/test_pass219_i158_typed_domain_join_execution.py`
- `benchmarks/pass219/pass219_i158_typed_domain_join_execution_benchmark.py`
- `contracts/pass219/PASS_219_I158_TYPED_DOMAIN_JOIN_EXECUTION_1_0.json`
- `docs/pass219/PASS_219_I158_TYPED_DOMAIN_JOIN_EXECUTION_1_0.md`
- `hhs_runtime/hhs_service_registry_v1.py`
- `.github/workflows/pass219-i158-typed-domain-join-execution.yml`
- this restart record.

## Public runtime surface

```text
module:
hhs_runtime.pass219.typed_domain_join_executor

functions:
project_rational_to_modular
execute_typed_domain_joins
typed_domain_join_executor_self_test

service:
runtime.pass219.typed_domain_join_execution
```

## Exact conformance candidate

```text
P = 30
p = 29
q = 31
Delta = 1
t = 30
m = 267
s = 2/25
f = 900
At = 1
Bt = 1
x = 18
y = 54
z = 18
w = 54
```

Exact harmonic segment:

```text
t^3-t                     = 26970
P^3-P/(P^2-pq)            = 26970
(t^3-t)/Delta             = 26970
P^2(MOD)(pq)              = [1] mod 899
m^2-m                     = 71022
(m^2-m) projected mod 899 = [1] mod 899
```

## Projection semantics

For rational `n/d` and modulus `m`, when
`gcd(d,m)=1`:

```text
pi_m(n/d) = n * inv(d) mod m
```

The witness retains:

- exact numerator and denominator;
- exact modular inverse;
- target modulus;
- projected representative;
- modular-state representative;
- candidate binding SHA-256;
- complete projection audit.

It explicitly records:

```text
injective = false
reverse inference = false
ordinary scalar remainder identity = false
scalar coercion = false
floating point authority = false
```

A noninvertible denominator remains `UNRESOLVED`.

A class mismatch is `REJECTED`.

## Expected join transition

```text
I157:
PROVED      = 5
UNRESOLVED  = 5
REJECTED    = 0

I158 expected:
PROVED      = 7
UNRESOLVED  = 3
REJECTED    = 0
```

Newly resolved:

```text
edge 2 — T3_MINUS_T_OVER_DELTA -> P2_MOD_PQ
edge 3 — M2_MINUS_M -> P2_MOD_PQ
```

## Remaining blockers

```text
edge 7
AB_ROOT_CORRESPONDENCE
BOUNDARY_PRODUCT_BINDING_REQUIRED

edge 8
MONOLITHIC_BOUNDARY_EQUALITY
COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED

edge 9
DELTA_RADICAL_PROJECTION
PASS191_X_SQUARED_PHASE_BINDING_REQUIRED
```

The Pass191 manifold kernel currently carries:

`"x_squared_binding": None`

I158 verifies this repository condition before retaining edge 9 as unresolved.

The Pass169 contract is also checked for the continued requirements for:

- symbolic radical construction;
- exact algebraic equality;
- VM81 canonical execution;
- Hash72 execution receipt.

## Authority boundary

```text
typed join execution complete         = false
canonical monolithic boundary proof   = false
Pass169 terminal proof                = false
VM81 execution verified               = false
VM81 mutation authority               = false
Hash72 execution receipt verified     = false
Hash72 mint authority                 = false
Hash216 persistence authority         = false
deterministic replay verified         = false
floating point authority              = false
```

No unresolved graph can advance into canonical mutation.

## Fixed geometry

Unchanged:

```text
target             = 72^42 = 5184^21
working manifold   = 3*72^72
route multiplicity = 3*72^30
required work bound= 7*W_baseline >= 81*W_effective
```

No physical full-manifold enumeration is claimed.

## Validation plan

Dedicated workflow:

`Pass 219 I158 Typed-Domain Join Execution`

Required gates:

1. Python parse/compile;
2. reject approximate/scalarizing paths;
3. dependency-scoped I158 tests;
4. public self-test;
5. deterministic benchmark;
6. exact modular witness assertions;
7. three-blocker assertion;
8. authority-boundary assertion;
9. artifact upload.

After feature green:

1. seal feature evidence;
2. reconcile current main;
3. open ready PR;
4. merge with expected-head guard after scoped green;
5. verify exact functional main;
6. run/collect I151 benchmark-history append;
7. seal exact-main evidence/history on evidence-only branch;
8. merge evidence seal without recursive I151/I158 trigger.

## Next boundary

`BOUNDARY_VALUE_EVALUATOR_AND_PHASE_EXPONENT_BINDING`

Required next work:

1. exact source-bound A/B product evaluator;
2. complete monolithic A/B boundary execution;
3. exact Pass191 x^2 phase-exponent binding;
4. only then Pass169 VM81 admission / Hash72 / Hash216 / replay.


## Repair-forward after first scoped validation

First dedicated run:

- run: `33783511319`
- job: `100742628579`
- validation head: `d9d1d60e0afe638e8565d123e14b7b81153c1522`
- conclusion: FAILURE
- failing stage: dependency-scoped pytest
- classification: `SEMANTIC_FALSIFICATION_NOT_INFRASTRUCTURE_FAILURE`

The failure proved the original I158 conventional modular interpretation was invalid for the frozen source.

Exact counterexample:

```text
P=30
pq=899
(t^3-t)/Delta = 26970 = 30*899
26970 mod 899 = 0
P^2 mod 899 = 900 mod 899 = 1
```

Therefore conventional residue equality cannot clear edge 2.

Repository formal typing rules already require the `Mod` glyph to be typed before conventional interpretation. I158 was repaired so conventional rational-to-modular projection is diagnostic only.

Repair commits:

- `643ed5e76f61db53073eddb2090ca6d2f785fd56` — preserve modular pivots as unresolved and bind formal typing protocol.
- `e497efd9575d8791f66e83e968aeb3faf10d7ed3` — correct diagnostic match/mismatch counts.
- `f77a295ea1ce69719946b4f621abce32acd3439c` — repair scoped tests.
- `882b6defbe17add14d3c5b8597506e0d0051701f` — repair benchmark.
- `9ca26361b5f3331b43a7bd05023d47d1322a07b8` — repair I158 contract.
- `cd8c353a25fc09b6fdb555687435f80d9709d4a1` — repair service registry.
- `c4372e8822eb13d107d223df6040db21c462d8ae` — repair documentation.
- `50d1617eb6aa0b467fd5a71632b79cddab52c2c7` — repair dedicated CI assertions.

Repaired expected state:

```text
PROVED = 5
UNRESOLVED = 5
REJECTED = 0
newly authorized modular pivots = 0
conventional diagnostic matches = 1
conventional diagnostic mismatches = 1
decision = UNRESOLVED_TYPED_SEMANTICS
```

Five explicit blockers:

```text
edge 2 HARMONICODE_MODULAR_PIVOT_SEMANTICS_REQUIRED
edge 3 HARMONICODE_MODULAR_PIVOT_SEMANTICS_REQUIRED
edge 7 BOUNDARY_PRODUCT_BINDING_REQUIRED
edge 8 COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED
edge 9 PASS191_X_SQUARED_PHASE_BINDING_REQUIRED
```

Repaired next boundary:

`REGISTER_HARMONICODE_MODULAR_PIVOT_BOUNDARY_AND_PHASE_BINDINGS`

Next action: run only the dedicated I158 workflow from the repaired head; if green, seal feature evidence and integrate.
