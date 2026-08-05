# Pass 213 — Iterations 1–6

Pass 213 builds a timestamp-bound authenticated compiled ROM, corrects carriers before interpretation, protects admitted entries in native memory, reuses compatible transformations through dependency-scoped validation, preserves the inventory across restarts, and signs persistent checkpoints with independent post-quantum authorities.

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
- root-bound deletion authorizations and retained tombstones;
- reconciliation between persistent state and native protected memory;
- retained-carrier and checkpoint recovery;
- authenticated checkpoint continuity and reopen validation.

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

### Iteration 6 — post-quantum signed checkpoints

- pinned `liboqs-python 0.16.0` and matching liboqs runtime;
- ML-KEM-768 recovery authority;
- ML-DSA-65 operational checkpoint authority;
- SLH-DSA SHA2-128s archival checkpoint authority;
- one sealed native secret-key arena per authority;
- authenticated public verifier bundle;
- dual signatures over one canonical checkpoint message;
- append-only signed-checkpoint root continuity;
- ML-KEM/HKDF-SHA-256/AES-256-GCM recovery capsules;
- verifier-only chain replay without secret-key access;
- signed-envelope, public-key, and capsule tamper detection;
- zeroization and destruction of all PQC secret-key arenas.

```text
Iteration 5 checkpoint
+ prior signed checkpoint root
+ signed sequence
+ verifier bundle
→ ML-DSA operational signature
→ SLH-DSA archival signature
→ signed checkpoint root
```

```text
ML-KEM-768 shared secret
→ HKDF-SHA-256 bound to checkpoint and AAD
→ AES-256-GCM recovery-key capsule
→ persistent capsule root
```

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The dedicated workflow builds the native C arena, verifies the required real liboqs mechanisms, executes every Iteration 1–6 test module, compiles every Pass 213 runtime module, validates the machine-readable contract, and retains the complete validation transcript as a workflow artifact.

Repository-native Iteration 6 evidence:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31036482697
job: 92409747663
validated head: e9ddcb09d3af525018a9e0196d065107c00674fc
conclusion: SUCCESS
```

## Current boundary

Pass 213 remains incomplete. Trusted external timestamp anchoring, full tensor invariants, API/CLI surfaces, governed native dispatch, performance evidence, final integration, merge, and verified-main closure remain subsequent work.
