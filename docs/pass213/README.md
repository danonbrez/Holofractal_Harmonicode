# Pass 213 — Iterations 1–3

Pass 213 builds the timestamp-bound authenticated compiled ROM, corrects its physical carriers before interpretation, and stores admitted entries in native protected memory.

## Iteration 1: compiled-ROM authority

Implemented:

- exact canonical serialization and framed SHA-256 identities;
- HMAC-SHA-256 domain-separated key derivation;
- integer-nanosecond opening and closing boundaries;
- authenticated noncommutative operation-group chaining;
- deterministic keyed full-cycle permutations;
- immutable compiled-ROM records;
- exact lookup, inventory roots, and deterministic receipts.

## Iteration 2: recovery-gated admission

Implemented:

- Pass 212 physical shard and parity protection;
- keyed Pass 213 carrier roots and authentication;
- correction of one or two missing shards within the inherited budget;
- fail-closed rejection outside the budget;
- recovered payload Hash216 validation before JSON deserialization;
- immutable entry Hash216 validation after deserialization;
- keyed `RecoveredROMAdmission` proofs;
- recovery-gated canonical insertion.

Canonical sequence:

```text
validate carrier
→ correct physical damage
→ validate reconstructed payload Hash216
→ deserialize
→ validate compiled-entry Hash216
→ mint admission proof
```

## Iteration 3: native secure memory

Implemented native C arena:

- `mmap` allocation with two `PROT_NONE` guard pages;
- non-executable data pages;
- `mlock` no-swap enforcement;
- `MADV_DONTDUMP` core-dump exclusion;
- `MADV_DONTFORK` child-process exclusion;
- `PR_SET_DUMPABLE` process hardening;
- constant-time 256-bit owner-token authorization;
- bounds-checked internal reads and writes;
- read-only sealing;
- explicit zeroization and zero verification;
- zeroization before unmap and release.

Implemented runtime surfaces:

- `NativeSecureArena` with no public raw-address surface;
- keyed `ALLOCATE`, `WRITE`, `SEAL`, `ZEROIZE`, and `DESTROY` receipts;
- `NativeProtectedCompiledROMStore`, which accepts only validated recovered admissions;
- sealed native storage of canonical compiled-entry bytes;
- internal lookup deserialization and Hash216 revalidation;
- inventory roots binding admission, arena, length, and receipt commitments;
- complete zeroizing retirement of protected entries.

End-to-end sequence:

```text
Pass 212 correction
→ recovered admission
→ native guarded allocation
→ bounded write
→ read-only seal
→ internal Hash216 verification
→ protected compiled-ROM lookup
→ zeroizing retirement
```

## Validation

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

The gate builds the C source with `-Wall -Wextra -Werror`, executes every Pass 213 test module, compiles all runtime modules, and validates the JSON contract.

## Current boundary

Pass 213 remains incomplete. Parametric delta validation, persistent tombstones, PQC enclosure, trusted external timestamps, full tensor invariants, API/CLI/native dispatch, performance evidence, final integration, merge, and verified-main closure remain subsequent work.
