# Pass 219 I159 — Harmonicode Modular Pivot Phase Binding Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ c36063ff649863d5fcda0dbeabed83c006ebe2f8`
- Branch: `agent/pass219-i159-harmonicode-modular-pivot-phase-binding`
- Merge target: `main`

## Purpose

I159 implements the missing typed execution adapter for the two I158 modular-pivot joins without conventional scalar remainder coercion.

Inherited anchors:

- Pass157 parser node: `HHS_MODULAR_NORMALIZATION`
- Pass157 node fields: `authority=P^2`, `state=pq`
- Pass157 exact modular phase identity: `n=qM+r`, `0<=r<M`
- Pass157 rule: quotient and residue are both retained; residues alone are never authoritative
- Appendix E typed closure relation: closure residue and renewed unit are distinct typed views of a completed closure event
- I157 rule: a typed constraint join may be proved without asserting untyped scalar identity

## Planned exact profile

For the frozen exact chain when `Delta=1`:

```text
M = pq = P^2-1
(t^3-t)/Delta = P*M
P^2 = 1*M + 1
```

Edge 2 profile:

`P_FOLD_CLOSURE_TO_RENEWED_UNIT`

with full phase witnesses:

```text
left lane     = (quotient=P, residue=0)
authority lane= (quotient=1, residue=1)
```

Edge 3 profile:

`RENEWED_UNIT_PHASE_CLASS_JOIN`

requires:

```text
m^2-m = k*M+1
```

with exact integer `k` retained.

No rule will identify the ordinary scalar values themselves.

## Authority boundary

I159 SHALL NOT claim VM81 execution, VM81 mutation, Hash72 mint, Hash216 persistence, canonical Pass169 proof, or deterministic replay.

## Validation plan

- exact parser-node inheritance binding
- exact full quotient/residue witnesses
- edge 2 positive/negative tests
- edge 3 positive/negative tests
- no residue-only authority
- no scalar equality claim
- I157 graph tamper rejection
- dependency-scoped pytest
- deterministic benchmark
- restart/evidence sealing

## Current validation state

Not yet executed.

## Next action

Implement the typed modular-pivot profile and integrate it into the I158 join membrane.
