# Pass 220 I011 restart checkpoint — Möbius quarter-phase / harmonic closure

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — DEPENDENCY-SCOPED CI QUEUED**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- merge target: `main`
- PR: #491
- predecessor I010 head before this task: `17a65f9c4b5cbb4c26cb563dee3988681b6d488f`
- I011 preimplementation checkpoint: `25ada2612bcfa3ea9cd44002a347198dd9c3b4b2`

## Implemented commits

- `467af2d68d06d1fa5cb0e0d65d2227cb4a9a1213` — exact Möbius/quarter-phase/harmonic witness
- `b8dd88260a9aa62b0746adce68671c5d7dbbd459` — dependency-scoped tests
- `96100533d99facb38d8000fcd3292e5d0b3d3042` — I011 formalization
- `e3053d76a9b4e35dcd7497ecb9e38d6f4d81b3ad` — dedicated CI workflow

## Implemented surfaces

### Möbius C4 circuit

```text
C(m)=(m-1)/(m+1)
C^2(m)=-1/m
C^4(m)=m
```

with exact inverse

```text
m=(1+rho)/(1-rho).
```

The exact projective matrix witness verifies:

```text
M=[[1,-1],[1,1]]
M^2=[[0,-2],[2,0]]
M^4=-4I ~ I
```

and indexes the orbit at `0,18,36,54,72 mod 72`.

### Harmonic phase closure

```text
(xy)(zw)/(xy+zw)=1
<=> (xy)(zw)=xy+zw
<=> 1/(xy)+1/(zw)=1
<=> (xy-1)(zw-1)=1
```

with involution

```text
T(r)=r/(r-1)
T^2(r)=r.
```

The exact translated parameterization is:

```text
xy=1+lambda
zw=1+lambda^-1.
```

### VM81 fold

Nine local nucleus pairs are evaluated independently. Global projection admits only when every local harmonic predicate closes:

```text
G_VM81 = AND(G_0 ... G_8)
```

One incoherent nucleus produces `REJECT_HARMONIC_INCOHERENCE`.

### Exact golden/norm bridge

The module carries `phi^2=phi+1` in exact `Q(sqrt(5))` Fraction-pair arithmetic and verifies:

```text
F(m)=m^4-3m^3-m-1
G(rho)=rho^4+3rho^3+rho-1

(1-rho)^4 F((1+rho)/(1-rho)) = 4 G(rho)
```

without floats.

## Files added

- `hhs_runtime/hhs_pass220_mobius_quarter_phase_v1.py`
- `tests/pass220/test_hhs_pass220_mobius_quarter_phase_v1.py`
- `docs/pass220/PASS_220_I011_MOBIUS_QUARTER_PHASE_HARMONIC_CLOSURE.md`
- `.github/workflows/pass220-i011-mobius-quarter-phase.yml`
- `docs/operations/restart/PASS_220_I011_MOBIUS_QUARTER_PHASE_PREIMPLEMENTATION_CHECKPOINT.md`
- this checkpoint

## Validation

Dedicated workflow:

- name: `Pass 220 I011 Möbius Quarter Phase`
- run: `35389299991`
- observed status at checkpoint preparation: `queued`

No green result is claimed yet.

The test surface contains 12 focused tests covering exact inverse/C4 closure, quarter-phase indexing, harmonic involution, symmetric/generic branches, fail-closed negatives, exact `Q(sqrt(5))`, norm covariance, and nine-nucleus VM81 coherence.

## Authority / honesty boundaries

- exact integer/Fraction/quadratic-extension arithmetic only;
- float input rejected;
- `E^(I Pi)`, `E^(-Pi)`, and `u^72` remain distinct typed surfaces;
- no numeric manufacture of symbolic poles;
- receipts are projection/witness records;
- `canonical_admission_authority=false`;
- no new VM81, Hash72, Hash216, persistence, or mutation authority.

## Remaining validation

Inspect only run `35389299991` and any directly impacted PR checks. If the I011 job fails, repair forward from this checkpoint. Do not rerun unaffected historical validation.

## Next action

After I011 dependency-scoped CI is green, bind the local harmonic predicate to the native VM81/Lane-5 admission call site only if that integration preserves the existing singleton mutation authority and ordered phase semantics. Then update the Pass 220 cumulative report and reconcile PR #491 against current main.
