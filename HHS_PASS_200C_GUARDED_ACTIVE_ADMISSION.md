# HHS PASS 200C — GUARDED ACTIVE ADMISSION AND CONTINUOUS EXACT ROLLBACK

Contract identifier: `HHS-P200C-CANARY-EVIDENCE-ACTIVE-GUARD-VM81-H72`

Classification target: `HHS_PASS_200C_GUARDED_ACTIVE_ADMISSION_VERIFIED`

## 1. Purpose

Pass 200C advances a proof-carrying optimization from completed Pass 200B canary evidence into a guarded active frontier.

Active execution means the candidate becomes the default returned path only after an exact guard passes on every invocation. It is not an unguarded or permanent compiler rewrite.

Pass 200C implements:

- aggregation of independent completed canary evidence;
- rejection of bundles with canary rollback history;
- explicit compiler, runtime, and operations approvals;
- one separate singleton VM81 activation receipt;
- immutable active-frontier history;
- bounded active leases;
- candidate return after exact result, witness, and replay equality;
- automatic reference restoration on mismatch, expiry, or lease exhaustion;
- explicit rollback;
- restart persistence and Hash72 event-chain verification.

## 2. Inherited authority

Pass 200C inherits:

- Pass 200A immutable compiler-candidate bundles and exact shadow evidence;
- Pass 200B dual-approved canary admission, immutable canary history, bounded counters, and fail-closed rollback;
- Pass 190 VM81 mutation admission and Hash72 receipts.

The candidate cannot authorize itself, generate an approval, select its evidence, modify the lease, extend expiry, suppress the exact guard, or write the current frontier pointer.

## 3. Canary evidence membrane

A bundle may be considered for active admission only when:

1. its Pass 200A status remains `COMPILER_CANDIDATE`;
2. Pass 200B event-chain verification succeeds;
3. at least two distinct canary frontiers for the same bundle completed through `EXHAUSTED` reference restoration;
4. each selected canary contains exactly its admitted invocation limit;
5. every selected invocation reports exact result, witness, and replay equality;
6. each selected canary's actual candidate-return ordinals match its exact integer ratio;
7. selected canaries have distinct frontier Hash72 identities;
8. selected canaries have distinct VM81 activation receipts;
9. their combined invocation coverage is at least 12;
10. no Pass 200B rollback frontier exists for the bundle.

The selected evidence snapshot binds:

- bundle and proof identities;
- canary and exhausted frontier identities;
- invocation roots;
- activation receipts;
- candidate and reference return totals;
- the Pass 200B event-chain tip.

## 4. Active approval membrane

Active admission requires exactly three approvals:

- `COMPILER_ACTIVE_APPROVE`;
- `RUNTIME_ACTIVE_APPROVE`;
- `OPERATIONS_ACTIVE_APPROVE`.

The approvals must use three distinct principals and three distinct VM81 receipt identities. Each approval is bound to:

- the immutable bundle Hash72;
- the immutable canary-evidence Hash72;
- the exact current Pass 200C frontier Hash72;
- an unexpired authority time.

A fourth, separate VM81 receipt authorizes the singleton active-frontier transition.

## 5. Immutable active frontier

An admitted frontier records:

- mode `ACTIVE_GUARDED`;
- bundle, proof, and canary-evidence identities;
- the three approval records;
- the singleton activation receipt;
- exact lease invocation limit;
- exact expiry;
- `guard_every_invocation=true`;
- `candidate_is_default_return_after_exact_guard=true`;
- `candidate_self_authorization=false`;
- `automatic_frozen_constraint_promotion=false`.

Existing frontiers are never rewritten or deleted.

Pass 200C frontier modes are:

- `REFERENCE`;
- `ACTIVE_GUARDED`;
- `LEASE_EXHAUSTED`;
- `ROLLED_BACK`.

## 6. Continuous exact guard

Every active invocation executes both the reference and candidate observation paths and compares:

- canonical exact result serialization;
- complete witness Hash72;
- deterministic replay Hash72.

The candidate is returned only when all three comparisons match. The reference path is returned on any mismatch.

The canonical condition is:

```text
exact_result_match
AND witness_match
AND replay_match
```

No sampled or periodic guard is permitted in Pass 200C. The guard runs on every active invocation.

## 7. Active lease

Every active admission has an exact integer invocation limit between 1 and 64 and an expiry.

The invocation counter is stored separately from the immutable frontier. It is incremented transactionally with the invocation record.

The final exact invocation may return the candidate when its guard passes, after which the authority creates a `LEASE_EXHAUSTED` reference frontier. A new active lease requires new approvals and a new singleton activation receipt.

## 8. Automatic rollback

Any exact-result, witness, or replay mismatch performs these actions atomically:

1. persist the failed invocation;
2. increment the active counter;
3. return the reference result;
4. create an immutable `ROLLED_BACK` frontier;
5. bind rollback to the invocation VM81 receipt;
6. update the singleton authority pointer to reference execution.

Expiry restores a reference frontier before any candidate result is returned.

## 9. Explicit rollback

Only the current `ACTIVE_GUARDED` frontier may be explicitly rolled back. The request requires its exact frontier identity and a fresh VM81 rollback receipt.

Stale frontier identifiers and non-active modes fail closed.

## 10. Frozen-constraint boundary

Pass 200C does not freeze an optimization as a permanent compiler or runtime constraint.

It does not authorize:

- removal of the reference path;
- removal or sampling of the exact guard;
- automatic lease renewal;
- automatic `FROZEN_CONSTRAINT` promotion;
- rewriting prior frontier or invocation history.

Permanent freezing requires a separate pass based on completed guarded-active evidence.

## 11. Persistence

The durable state includes:

- immutable canary-evidence snapshots;
- immutable active and reference frontiers;
- separate active counters;
- immutable active invocation records;
- the singleton current-frontier pointer;
- the ordered Hash72 event chain.

Restart must preserve all identities, counters, return totals, and event-chain tip.

## 12. Acceptance criteria

Pass 200C closes only when validation proves:

- two successful canaries and at least 12 exact canary invocations are required;
- a canary rollback disqualifies its bundle;
- three distinct approval principals, capabilities, and receipts are required;
- a separate singleton activation receipt is required;
- active candidate return occurs only after every exact guard passes;
- mismatch and expiry return reference and restore a rollback frontier;
- lease exhaustion restores reference execution;
- stale frontier operations fail closed;
- frontier tampering is rejected;
- restart preserves evidence, frontiers, counters, invocations, and event-chain tip;
- no floating-point canonical operation occurs;
- frozen-constraint promotion remains disabled.
