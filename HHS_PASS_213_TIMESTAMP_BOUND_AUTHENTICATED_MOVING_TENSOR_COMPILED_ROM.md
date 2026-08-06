# HHS Pass 213 — Timestamp-Bound Authenticated Moving Tensor Compiled ROM and Runtime Memory Integrity Kernel

**Contract:** `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`  
**Status:** `CONTRACT AUTHORIZED — IMPLEMENTATION IN PROGRESS`  
**Current iteration:** `10`

## Binding inheritance

Pass 213 is an in-place upgrade of the complete pre-pass foundation and Passes 001–212. Iteration 10 inherits every validated Iteration 1–9 authority without replacement.

## Cumulative canonical path

```text
untrusted carrier
→ Pass 212 physical correction
→ reconstructed Hash216 validation
→ immutable compiled-ROM admission
→ sealed native protected memory
→ exact or dependency-scoped reusable admission
→ persistent inventory / tombstones / recovery
→ ML-DSA + SLH-DSA signed checkpoint
→ ML-KEM recovery enclosure
→ RFC 3161 trusted timestamp anchor
→ exact moving-tensor derivation
→ governed projection API/CLI
→ exact protected compiled-ROM dispatch admission
→ allocation-free fixed-width C execution
→ successor Hash216 + ordered Hash72 receipt
→ authenticated persistent execution ledger
```

## Retained Iterations 1–9

1. Immutable Hash216 compiled-ROM identity, integer timestamp boundaries, noncommutative operation chains, closure paths, and Hash72 receipts.
2. Pass 212 correction and reconstructed-payload validation before interpretation or insertion.
3. Guarded, locked, sealed, non-executable native arenas with owner authorization and verified zeroization.
4. Typed parametric templates, exact deltas, dependency-scoped revalidation, and authenticated witness reuse.
5. SQLite WAL inventories, append-only `ADMIT`, `RECOVER`, and `TOMBSTONE` roots, unexplained-absence detection, and retained recovery material.
6. ML-KEM-768 recovery, ML-DSA-65 operational signatures, SLH-DSA SHA2-128s archival signatures, protected keys, and verifier-only replay.
7. RFC 3161 external timestamp anchors bound to signed checkpoints, verifier roots, prior anchors, Hash216 lineage, local boundaries, and TSA evidence.
8. Exact Lo Shu, Sudoku, and Fibonacci moving tensors; reversible VM5184×G243 and 50,388,480-position maps; exact closure proofs; Hash216 roots; Hash72 receipts; keyed replay; derived-only floating projections.
9. Shared capability-governed API/CLI public projections, authenticated append-only projection storage, source/projection receipt separation, strict protected-field rejection, and no raw-state or unsafe mutation exposure.

## Iteration 10 — governed native compiled dispatch

Iteration 10 turns prevalidated compiled-ROM entries into executable native operations without bypassing the protected-memory, timestamp, tensor, policy, lineage, and singleton VM81 authorities.

### Real native ABI

`native/pass213/hhs_pass213_native_dispatch.c` implements a versioned fixed-width C ABI with:

- no dynamic allocation;
- no ambient mutable state;
- at most eight unsigned-64 operands and four results;
- exact VM81 cell, operation-slot, and G243 route validation;
- deterministic status and result structures;
- warnings treated as errors in the cumulative build gate.

Implemented native operations are:

```text
hhs.native.u64.add.v1
hhs.native.u64.sub.v1
hhs.native.u64.xor.v1
hhs.native.u64.and.v1
hhs.native.u64.or.v1
hhs.native.u64.mul_mod.v1
hhs.native.u64.rotl.v1
hhs.native.u64.eq.v1
hhs.native.u64.select.v1
```

Modular multiplication uses an exact 128-bit intermediate before unsigned-64 reduction.

### Admission boundary

A native execution request is accepted only when all of the following match the current authority:

- exact protected compiled-ROM `entry_hash216`;
- exact operation identity and supported native dispatch identifier;
- current parent state Hash216;
- current kernel policy Hash216;
- current kernel measurement Hash216;
- current Hash216 lineage;
- current trusted timestamp anchor and monotonic integer-nanosecond request boundary;
- current moving-tensor root and domain;
- exact VM81 cell, operation slot, G243 control identifier, and hydration lane;
- compiled input and result counts;
- exact sorted read and write sets;
- compiled unsigned-64 operand maximum and optional modulus;
- current protected inventory root.

Stale-parent replay, duplicate replay, timestamp rollback, policy substitution, tensor substitution, lineage divergence, access-set mismatch, operand overflow, unsupported dispatch identifiers, and malformed native responses fail before state advancement.

### Hidden moving-tensor route

The canonical compiled entry supplies the logical VM5184×G243 route. For the full domain, the hydration lane extends it into one of `50,388,480` logical positions.

The current moving tensor derives the physical execution address internally. The logical address, physical address, tensor root, closure proof root, compiled entry identity, and route coordinates are committed into a route Hash216. The physical address itself never crosses the public surface.

### Singleton VM81 execution

One authority lock admits one execution at a time. Reentry is rejected before the C ABI is called. The protected compiled entry remains immutable before and after execution.

The native request contains only the compiled route, exact unsigned operands, request sequence, and optional modulus. Native execution cannot compile, repair, delete, read protected memory, alter tensor geometry, issue capabilities, or mutate the persistent ledger directly.

### Deterministic successor

Each successful execution derives:

```text
request_root_hash216
result_root_hash216
route_commitment_hash216
read_set_root_hash216
write_set_root_hash216
successor_state_root_hash216
receipt_hash72
```

The successor binds the prior state and receipt, request, result, route, access sets, tensor, policy, kernel measurement, lineage, and protected inventory root.

The ordered Hash72 receipt is emitted over the successor Hash216. The singleton VM81 state advances only after the execution event has been appended successfully to the authenticated ledger.

### Persistent execution ledger

`NativeDispatchLedger` uses SQLite WAL mode with `synchronous=FULL`. Every event stores canonical JSON, a Hash216 event root, and a keyed HMAC-SHA-256 authentication tag.

Every open and append verifies:

- exact contiguous sequence;
- prior receipt continuity;
- prior and successor state continuity;
- event-root integrity;
- authentication tag integrity;
- successor Hash72 validity;
- configured baseline state and receipt anchors.

Database mutation, receipt substitution, state-chain substitution, sequence gaps, wrong keys, and anchor substitution fail closed.

### Dispatch capabilities

Execution and receipt reads use a separate local capability authority:

```text
dispatch.execute
dispatch.read
```

Capabilities bind subject, exact scopes, issuance and expiration nanoseconds, epoch, nonce, and capability Hash216. Issuance is local CLI authority only; there is no network issuance route.

### HTTP routes

```text
GET  /api/runtime/native-dispatch/status
POST /api/runtime/native-dispatch/execute
GET  /api/runtime/native-dispatch/receipts/{sequence}
```

HTTP accepts either a Bearer token or `X-HHS-Dispatch-Capability`. Conflicting credentials fail closed. Responses use the inherited canonical runtime envelope.

### CLI parity

```text
hhs-pass213-dispatch status
hhs-pass213-dispatch execute
hhs-pass213-dispatch receipt
hhs-pass213-dispatch capability issue
```

HTTP and CLI invoke the same `GovernedNativeDispatchService`. Identical baseline state, request, capability claims, protected entry, and tensor context produce identical governed native results and successor commitments.

### Explicitly unexposed operations

Iteration 10 does not expose:

- compiled-ROM creation or replacement;
- protected memory reads or native pointers;
- repair, recovery mutation, deletion, or tombstone creation;
- tensor seeds, permutations, or physical addresses;
- retained carriers or recovery shards;
- RFC 3161 DER material;
- kernel keys or capability-authority keys;
- uncommitted candidate state.

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The cumulative gate:

- builds the secure arena and native dispatch C libraries with warnings as errors;
- verifies ML-KEM-768, ML-DSA-65, SLH-DSA SHA2-128s, AES-GCM, and OpenSSL RFC 3161 support;
- executes all 122 Iteration 1–10 tests;
- compiles every Pass 213 runtime, API, and CLI module;
- parses the machine-readable Iteration 10 contract;
- retains the full transcript.

Validated runtime evidence:

```text
head: af36575233248d77b606ff63b41ca5e51ca23ff5
workflow run: 31062363170
job: 92492790661
122 tests passed
artifact: pass213-iteration10-validation-31062363170
artifact digest: sha256:46689e6e95a99fdb1e241431809aad60d15778ea954567be22fe2de9010c3522
```

## Iteration boundary

Pass 213 remains nonterminal, draft, and unmerged. Remaining implementation work is full-hydration performance and recovery evidence followed by final integration, merge, and verified-main closure. Pass 214 must not merge ahead of authoritative Pass 213 closure.
