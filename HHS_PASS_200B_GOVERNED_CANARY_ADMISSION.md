# HHS PASS 200B — GOVERNED CANARY ADMISSION, BOUNDED EXECUTION, AND FAIL-CLOSED ROLLBACK

Contract identifier: `HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72`

Classification target: `HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_VERIFIED`

## 1. Purpose

Pass 200B advances a verified Pass 200A compiler-candidate bundle into a bounded canary frontier. It does not create unrestricted active execution and it does not freeze a compiler or runtime constraint.

The pass implements:

- explicit compiler and runtime promotion approvals;
- approval identity, capability, expiry, bundle, and frontier binding;
- one singleton VM81 activation receipt per canary frontier;
- immutable frontier history;
- bounded invocation counters;
- deterministic candidate-return selection;
- exact result, witness, and replay comparison;
- automatic fail-closed reference restoration;
- explicit operator rollback;
- restart persistence and Hash72 event-chain verification.

## 2. Inherited authority

Pass 200B inherits:

- Pass 200A independent holdout envelopes, immutable optimization bundles, and exact compiler-shadow matches;
- Pass 199 durable branch execution, complete replay, and singleton calibration commit;
- Pass 190 VM81 mutation admission and Hash72 receipts.

A Pass 200B candidate cannot authorize itself, create its own approval, change its own invocation limit, extend its own expiry, or write the authority frontier directly.

## 3. Admission membrane

A bundle may enter a canary frontier only when all of the following hold:

1. Pass 200A reports a closed proof authority.
2. The bundle status is `COMPILER_CANDIDATE`.
3. The bundle compiler mode is `SHADOW`.
4. At least one persisted Pass 200A shadow record for the bundle reports an exact match and zero candidate activation.
5. Exactly two approvals are present.
6. The approvals use distinct principals and distinct VM81 receipt identities.
7. The approval capabilities are exactly:
   - `COMPILER_PROMOTION_APPROVE`;
   - `RUNTIME_PROMOTION_APPROVE`.
8. Each approval is bound to:
   - the immutable bundle Hash72;
   - the current frontier Hash72;
   - an unexpired authority time;
   - its own VM81 receipt Hash72.
9. A separate VM81 activation receipt authorizes the singleton frontier transition.
10. No prior canary frontier remains open.

Any failed condition rejects admission without changing the current frontier.

## 4. Immutable frontier chain

Every authority transition creates a new immutable frontier record. Existing frontier records are never rewritten or deleted.

The frontier modes implemented by Pass 200B are:

- `REFERENCE` — the initial reference-only frontier;
- `CANARY` — a bounded candidate-return frontier;
- `ROLLED_BACK` — reference restoration following mismatch, expiry, or explicit rollback;
- `EXHAUSTED` — reference restoration after the exact invocation limit is reached.

Each record binds:

- its predecessor frontier identity;
- the restored frontier identity where applicable;
- bundle and proof identities where applicable;
- transition reason;
- VM81 activation or transition receipt;
- a Hash72 frontier identity;
- its Hash72 event-chain record.

The mutable invocation counter is stored separately from the immutable frontier body.

## 5. Bounded canary selection

A canary frontier declares exact integer values:

- `invocation_limit`, where `1 <= invocation_limit <= 64`;
- `canary_numerator`;
- `canary_denominator`, where `1 <= numerator <= denominator`.

For zero-based invocation ordinal `n`, candidate return is selected when:

```text
n MOD canary_denominator < canary_numerator
```

Selection alone never permits candidate return. Exact validation must also pass.

The invocation counter is incremented transactionally and cannot exceed the admitted limit. Reaching the limit creates an immutable `EXHAUSTED` frontier and restores reference-only execution.

## 6. Exact invocation comparison

Before any selected canary invocation may return the candidate path, Pass 200B compares:

- canonical exact result serialization;
- complete witness Hash72;
- deterministic replay Hash72.

The comparison contains no floating-point canonical operation.

A candidate result is returned only when:

```text
selected
AND exact_result_match
AND witness_match
AND replay_match
```

Otherwise, the reference result is returned.

## 7. Automatic rollback

Any exact-result, witness, or replay mismatch performs these actions in one authority transaction:

1. persist the failed invocation record;
2. increment the bounded counter;
3. create a `ROLLED_BACK` reference frontier;
4. bind the rollback to the invocation VM81 receipt;
5. update the singleton authority pointer to the reference frontier;
6. return the reference result.

An expired canary also restores the reference frontier before any candidate return.

Rollback is repair-forward. The failed canary and all prior frontier records remain available for audit and replay.

## 8. Explicit rollback

An operator may explicitly roll back only the currently active canary frontier. The request must carry a fresh VM81 rollback receipt and the exact current frontier identity.

A stale frontier identifier, non-canary current mode, or invalid receipt fails closed.

## 9. Compiler and runtime boundary

Pass 200B permits bounded canary return only inside the admitted frontier.

It does not implement:

- automatic promotion to unrestricted `ACTIVE` execution;
- automatic promotion to `FROZEN_CONSTRAINT`;
- candidate self-authorization;
- candidate canonical commit;
- approval renewal by the candidate;
- invocation-limit mutation after admission.

A later pass must independently authorize unrestricted active admission.

## 10. Persistence and replay

The durable state includes:

- immutable frontiers;
- bounded canary counters;
- immutable invocation records;
- the singleton current-frontier pointer;
- the ordered Hash72 event chain.

Restart must preserve:

- current frontier identity;
- invocation usage;
- candidate and reference return counts;
- rollback and exhaustion history;
- event-chain tip.

Any persisted frontier-body modification must be detected by Hash72 verification.

## 11. API and visual projection

The governed API prefix is:

```text
/api/runtime/optimization-canary
```

It provides:

- status;
- explicit admission;
- verified canary probe;
- explicit rollback;
- frontier history;
- invocation history;
- verification;
- governed tool projection.

The visual panel may request these operations but is not authority. It cannot manufacture approvals, receipts, frontier identities, or comparison results.

## 12. Acceptance criteria

Pass 200B closes only when validation proves:

- two distinct principals and capabilities are required;
- stale, duplicate, expired, and tampered approvals are rejected;
- each canary frontier has exactly one activation commit;
- invocation counters never exceed the admitted limit;
- deterministic candidate selection matches the admitted ratio;
- exact matches permit only selected candidate returns;
- mismatches return reference and restore a rollback frontier;
- expiry restores reference execution;
- explicit rollback restores reference execution;
- exhaustion restores reference execution;
- frontier and event tampering are rejected;
- restart preserves counters, frontiers, invocations, and event-chain tip;
- no floating-point canonical operations occur;
- unrestricted active and frozen-constraint promotion remain disabled.
