# Pass 219 RML18 transport conservation acceleration restart

## Repository-visible restart state

- Base lineage: `agent/pass219-recursive-manifold-learning-20260909`
- Base commit: `eea9fcf5fa90589cb9adf2b26260af50e10fb377`
- Frozen RML17 tree: `7f6271f39bda52a24946ac7d2786f8be8b93a3dd`
- Working branch: `agent/pass219-rml18-transport-conservation-acceleration-20260910`
- Merge target: `agent/pass219-recursive-manifold-learning-20260909`
- Pass: `219`
- Iteration: `RML18_TRANSPORT_CONSERVATION_ACCELERATION`

## Frozen equality baseline

RML17 is closed and immutable for RML18. The RML18 pass may profile and add
candidate acceleration above RML17, but it may not weaken, rewrite, bypass, or
replace any RML17 conservation predicate.

The frozen operator baseline remains:

```text
Div_H(s) = 0
J(s,d) = -J(T_H(s,d), d^-1)
C(s) = 1 and T_H(s,d) = s' => C(s') = 1
nu_H L_H = 0
R^-1(R(s)) = s
Delta_loss = 0
```

The frozen finite transport surface remains exactly:

```text
4 x 64 x 72 x 81 = 1,492,992 addresses
```

## RML18 1.001 invariant rule

The user-specified RML18 admission token is the exact rational value
`1001/1000`, rendered canonically as the string `1.001`. It is not represented
as a binary floating-point number and is not a timing score or residual.

Every accelerated candidate route or transport-state witness must return the
exact typed invariant:

```text
invariant_numerator   = 1001
invariant_denominator = 1000
invariant_decimal     = "1.001"
```

Only a candidate that independently satisfies the frozen RML17 equality gates
may receive that token. Any candidate that does not return exactly this token
is immediately classified:

```text
NULL/UNDEFINED
```

No degraded numerical value, epsilon band, approximate score, smoothing path,
or timing-derived substitute is admitted.

## Stage 1: profile before acceleration

Files introduced in the profiling checkpoint:

- `benchmarks/pass219/pass219_rml18_transport_conservation_profile.py`
- `.github/workflows/pass219-rml18-transport-conservation-profile.yml`
- this restart record

The profiler measures only observational latency for:

- the exhaustive RML17 1,492,992-address manifold audit;
- representative single-address audits;
- RML17 selected-route conservation audits;
- RML17 composed-route conservation audits.

Before profiling, the dedicated workflow re-runs the frozen RML17 test suite.
Timing is explicitly non-canonical and cannot affect admission.

## Planned acceleration stage

After the profile identifies the dominant cost, implement an additive RML18
candidate verifier. Expected optimization target is the finite address-manifold
conservation scan, because its topology is a Cartesian product of exact cyclic
operation/phase/cell coordinates with constant reciprocal signed flux.

Any shortcut must be proved against the frozen exhaustive RML17 result before
it is admitted. The accelerated path must remain read-only and must not gain
VM81 mutation, Hash72 mint, Hash216 persistence, floating-point, scalar
projection, or route-selection authority.

## Restart commands

```bash
PYTHONPATH="$PWD" python -m pytest -q \
  tests/pass219/test_pass219_rml17_discrete_transport_conservation.py

PYTHONPATH="$PWD" python \
  benchmarks/pass219/pass219_rml18_transport_conservation_profile.py \
  --output artifacts/pass219_rml18/rml18_transport_profile.json \
  --route-cases 6
```

## Completion criteria

RML18 closes only when:

1. frozen RML17 regression is green;
2. the profiler records the dependency-scoped baseline;
3. an acceleration candidate is implemented without modifying RML17;
4. candidate output is compared directly with the frozen RML17 equality gates;
5. exact `1001/1000 == "1.001"` admission is issued only for equality-preserving candidates;
6. all mismatches fail closed as `NULL/UNDEFINED`;
7. dependency-scoped benchmark evidence shows the acceleration result;
8. restart/evidence receipts are committed;
9. integration history is preserved into the canonical RML lineage.
