# Pass 213 — Iterations 1–7

Pass 213 builds a timestamp-bound authenticated compiled ROM, corrects carriers before interpretation, protects admitted entries in native memory, reuses compatible transformations through dependency-scoped validation, preserves the inventory across restarts, signs persistent checkpoints with independent post-quantum authorities, and anchors the resulting history through independently signed RFC 3161 timestamp tokens.

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

### Iteration 7 — RFC 3161 trusted external timestamp anchors

- canonical timestamp intent bound to the dual-signed checkpoint root;
- verifier-bundle, sequence, prior-anchor, Hash216-lineage, local-boundary, and authority binding;
- SHA-256 RFC 3161 message imprint;
- nonce-bearing DER timestamp requests;
- HTTP `application/timestamp-query` / `application/timestamp-reply` transport;
- isolated OpenSSL TSA transport for offline deployments and integration testing;
- explicit X.509 trust-bundle verification;
- retained DER request/response, TSA serial, policy, subject, nonce, and UTC generation time;
- append-only trusted timestamp-anchor roots;
- complete post-quantum and RFC 3161 reverification on persistent reopen;
- rejection of trust substitution, sequence gaps, prior-root changes, lineage substitution, time regression, serial reuse, and DER tampering.

```text
ML-DSA + SLH-DSA signed checkpoint
+ prior trusted timestamp root
+ Hash216 lineage
+ local nanosecond boundary
→ RFC 3161 message imprint
→ independent TSA signature
→ trusted timestamp anchor root
```

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The dedicated workflow builds the native C arena, verifies the real liboqs mechanisms, verifies OpenSSL RFC 3161 support, creates an actual local X.509 timestamp authority, executes every Iteration 1–7 test module, compiles every Pass 213 runtime module, validates the machine-readable contract, caches the matching native liboqs build, and retains the complete validation transcript.

Repository-native Iteration 7 implementation evidence:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31053828521
job: 92466865251
validated head: 67e36905679fe99f883b9500ec7efbe13e4abcf4
tests: 74 passed
result: SUCCESS
artifact: pass213-iteration7-validation-31053828521
artifact digest: sha256:948f8f200c39b11b52ec1738f36ea391fb1e043868f1908311c2e2ae5ffe6d2d
```

## Current boundary

Pass 213 remains incomplete. Full high-dimensional magic-square/Sudoku/Fibonacci tensor invariants, API/CLI surfaces, governed native dispatch, performance evidence, final integration, merge, and verified-main closure remain subsequent work.
