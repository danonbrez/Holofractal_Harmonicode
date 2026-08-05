# Pass 213 — Iterations 1–5

Pass 213 builds a timestamp-bound authenticated compiled ROM, corrects carriers before interpretation, protects admitted entries in native memory, reuses compatible transformations through dependency-scoped validation, and preserves their inventory across restarts.

## Implemented progression

### Iteration 1 — compiled-ROM authority

- immutable compiled-operation Hash216 identities;
- exact timestamp boundaries and noncommutative operation ordering;
- keyed closure paths, exact lookup, inventory commitments, and receipts.

### Iteration 2 — recovery-gated admission

- Pass 212 shard validation and bounded reconstruction;
- recovered-payload Hash216 before deserialization;
- immutable entry Hash216 after deserialization;
- keyed recovered-ROM admission proofs.

### Iteration 3 — native protected memory

- guarded non-executable native arenas;
- page locking, dump exclusion, and fork exclusion;
- constant-time owner authorization;
- read-only sealing and internal Hash216 revalidation;
- explicit zeroization before release.

### Iteration 4 — parametric delta admission

- immutable typed templates bound to protected compiled entries;
- complete candidate-shape and type validation;
- exact changed-field deltas;
- affected-constraint dependency closure;
- authenticated reuse of unaffected witnesses;
- timestamp-bound VM81 admissions in sealed native arenas.

### Iteration 5 — persistent inventory and tombstones

- SQLite WAL storage with full synchronization;
- append-only authenticated `ADMIT`, `RECOVER`, and `TOMBSTONE` events;
- deterministic successor inventory roots;
- persistent LIVE and TOMBSTONED identity sets;
- retained authenticated recovery carriers;
- separate deletion-authority key and root-bound authorizations;
- tombstone commitment before native zeroization;
- reconciliation between persistent state and protected native memory;
- unexplained absence detection;
- retained-carrier and checkpoint recovery;
- authenticated checkpoint chain and reopen validation.

```text
persistent LIVE identity
→ native presence check
├─ present: validate protected lookup
└─ absent: classify unexplained deletion
           → recover carrier/checkpoint
           → Pass 212 correction
           → restore sealed arena
           → append RECOVER root
```

```text
authorized retirement
→ deletion authorization bound to current inventory root
→ retained TOMBSTONE transition
→ successor root
→ native zeroization and destruction
```

## Validation

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

The gate builds the native C arena with `-Wall -Wextra -Werror`, executes every Iteration 1–5 test module, compiles every Pass 213 runtime module, and validates the machine-readable contract.

## Current boundary

Pass 213 remains incomplete. PQC enclosure and checkpoint signatures, external trusted timestamp anchoring, full tensor invariants, API/CLI surfaces, governed native dispatch, performance evidence, final integration, merge, and verified-main closure remain subsequent work.
