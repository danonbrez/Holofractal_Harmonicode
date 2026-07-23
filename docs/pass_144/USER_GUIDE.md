# HARMONICODE User Guide

## 1. What HHS is

HHS is a constraint-governed symbolic execution environment. A computation is admitted only when its typed operations, dependencies, authority, and closure witnesses satisfy the active invariant set.

The practical model is:

```text
input
→ canonical parsing
→ typed state construction
→ invariant admission
→ ordered execution
→ validation
→ receipt generation
→ replayable output
```

## 2. Exactness rules

Native execution uses exact integers, rational relations, symbolic roots, and typed operators. IEEE floating-point values are not authoritative native states unless an explicit external-control or projection contract admits them.

Do not assume that familiar glyphs have conventional scalar semantics. Operator meaning is determined by typed dispatch and local gate scope.

## 3. Equality gates

`==` is an admission/equivalence gate. It may establish that two lanes close to the same locally admitted state without making their full histories, types, or global meanings interchangeable.

## 4. Receipts

Every authoritative operation should expose enough evidence to identify:

- canonical input;
- ordered operator path;
- output;
- dependency ancestry;
- validation result;
- authority level;
- replay identity.

## 5. Safe use pattern

1. Construct exact inputs.
2. Call the documented runtime surface.
3. Inspect the classification and receipt.
4. Reject narrative success without a closed execution witness.
5. Replay when reproducibility matters.
6. Preserve parent artifacts and ancestry.

## 6. Common classifications

- `PROVED`: all required premises and goals closed through the active proof surface.
- `GOAL_NOT_PROVED`: premises admitted, but at least one goal remained open.
- `CONSTRAINT_FAILED`: one or more premises failed admission.
- `RECOVERY_CLOSED`: corrupted data was reconstructed and revalidated exactly.
- `UNRECOVERABLE_*`: the declared redundancy or authority boundary was exceeded.
- `SIMULATION_PROJECTION_ONLY`: output is a deterministic simulation projection, not empirical physical evidence.

## 7. Immutability

Pass 144 documentation does not modify prior runtime files. The parent-tree verifier must pass before the documentation release is accepted.
