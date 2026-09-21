# Pass 219 — H36 / Hash216 M-Exponent Lattice Start Checkpoint

Status: START CHECKPOINT / RESTARTABLE
Date: 2026-09-17

## Repository state

- Base/main commit: `9b36a5322dbb6a92c2879b4b8eb22f9da67a8c72`
- Branch: `pass219/h36-hash216-m-exponent-lattice-v1`
- Merge target: `main`
- Inherited theorem PR: `#486` merged before this branch was created.

## Authorized task

Implement the next Lane 5 cycle proving and exposing the direct shared `M` exponent geometry between Harmonic36, Hash72/Hash216, VM5184, and the Lo Shu seed without introducing a semantic translator.

Exact inherited identities to preserve:

```text
36  = 2^2 * 3^2
72  = 2^3 * 3^2
216 = 2^3 * 3^3
5184 = 72^2 = 2^6 * 3^4
M = 72^72 = 5184^36 = 2^216 * 3^144
```

Licensed Pythagorean/Lo Shu projection inherited from PR #486:

```text
a^2 = 1
b^2 = 2
c^2 = 3
P^4 = c^4 = 9
AB = P^4
1 = P^4 / 9
```

Lo Shu local exponent geometry to formalize:

```text
1 -> (0,0)
2 -> (1,0)
4 -> (2,0)
8 -> (3,0)
6 -> (1,1)
9 -> (0,2)
```

The `2,4,8` binary triangle is anchored at the shared `1` cell; `6 = 2*c^2 = 2*3` is the mixed binary/ternary even-corner state; `9=P^4` is the ternary-square/global licensed projection.

## Authority boundary

This cycle is metadata/proof/binding only. It MUST NOT add independent canonical mutation authority, Hash72 authority, Hash216 admission authority, persistence authority, or floating-point authority. Existing singleton VM81/Hash72 admission remains authoritative.

## Planned implementation

1. Add an exact C ABI witness for `(2,3)` exponent coordinates and the shared `M` manifold identities.
2. Bind the witness directly to the existing H36/Hash216 occurrence/transition surface; no translator layer.
3. Add Lo Shu local exponent-coordinate witnesses and `AB=P^4=9` projection metadata.
4. Add dependency-scoped C tests, including negative validation cases.
5. Wire the new ABI into the aggregate exact runtime and Harmonic36 CI.
6. Add white-paper/contract documentation and a closing restart checkpoint.

## Validation state at checkpoint

- PR #486 exact-head theorem validation: green before merge.
- New branch validation: not yet run.

## Next action

Implement the exact C witness and dependency-scoped tests, then run the existing Harmonic36 workflow at the exact branch head.
