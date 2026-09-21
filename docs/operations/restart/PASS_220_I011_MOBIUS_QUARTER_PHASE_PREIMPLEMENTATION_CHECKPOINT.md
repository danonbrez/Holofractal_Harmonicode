# Pass 220 I011 preimplementation checkpoint — Möbius quarter-phase / harmonic closure

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- base/head before this task: `17a65f9c4b5cbb4c26cb563dee3988681b6d488f`
- merge target: `main`
- PR: #491
- predecessor: `docs/operations/restart/PASS_220_I010_USER_APPROVED_VECTOR_CONTEXT_CHECKPOINT.md`

## Task

Implement the next exact formalization cycle for the Pass 220 Lo Shu/Pythagorean stack without widening canonical VM81/Hash72/Hash216 mutation authority.

The dependency-scoped target is:

```text
rho(m) = (m-1)/(m+1)
rho^2(m) = -1/m
rho^4(m) = m
```

and its exact bridge to:

```text
phase positions: 0,18,36,54,72 mod 72
harmonic channel closure: (xy)(zw)/(xy+zw) = 1
translated closure: (xy-1)(zw-1) = 1
VM81 fold: every one of nine nuclei must close locally before global AND-fold
```

## Planned files

- `hhs_runtime/hhs_pass220_mobius_quarter_phase_v1.py`
- `tests/pass220/test_hhs_pass220_mobius_quarter_phase_v1.py`
- `docs/pass220/PASS_220_I011_MOBIUS_QUARTER_PHASE_HARMONIC_CLOSURE.md`
- `.github/workflows/pass220-i011-mobius-quarter-phase.yml`
- postimplementation restart checkpoint

## Constraints

- exact `Fraction`/integer arithmetic only;
- no float authority;
- preserve ordered phase/harmonic semantics;
- fail closed on singular branches;
- receipts are witness/projection infrastructure only;
- no new canonical admission, persistence, Hash72, or Hash216 authority;
- do not flatten `E^(I Pi)`, `E^(-Pi)`, or `u^72` into one literal scalar.

## Validation plan

Run the new dependency-scoped pytest module in CI. Do not delay the restartable checkpoint on queued external CI; repair forward from the repository-visible state if a new impacted check fails.
