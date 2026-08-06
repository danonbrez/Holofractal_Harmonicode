# Pass 213 — Iterations 1–10

Pass 213 implements an authenticated compiled ROM whose carriers are corrected before interpretation, whose canonical entries live in protected native memory, whose reusable operations receive exact or dependency-scoped admission, whose inventory survives restarts with authorized tombstones and recovery, whose checkpoints are post-quantum signed, whose history is independently timestamped, whose execution geometry is selected by an exact moving tensor, whose externally visible state is capability-governed, and whose accepted compiled operations execute through a deterministic native C authority.

## Implemented progression

- **Iteration 1:** immutable compiled-ROM identity, integer timestamp boundaries, ordered operation chains, exact lookup, closure paths, and receipts.
- **Iteration 2:** Pass 212 correction and recovered Hash216 validation before compiled-entry decoding.
- **Iteration 3:** guarded, locked, sealed, non-executable native arenas with verified zeroization.
- **Iteration 4:** typed parametric templates, exact deltas, affected-only constraint validation, and authenticated witness reuse.
- **Iteration 5:** SQLite WAL inventory, append-only mutation roots, retained recovery carriers, tombstones, and unexplained-deletion detection.
- **Iteration 6:** ML-KEM-768 recovery, ML-DSA-65 operational signatures, SLH-DSA SHA2-128s archival signatures, protected keys, and verifier-only replay.
- **Iteration 7:** RFC 3161 external timestamp anchors bound to signed checkpoints, verifier roots, prior anchors, Hash216 lineage, local boundaries, and TSA evidence.
- **Iteration 8:** exact Lo Shu/Sudoku/Fibonacci moving tensors, reversible VM5184×G243 and full-hydration maps, closure proofs, Hash216 roots, Hash72 receipts, and keyed replay.
- **Iteration 9:** shared capability-governed API/CLI projections with authenticated public commitments, source/projection receipt separation, and strict protected-state non-exposure.
- **Iteration 10:** real fixed-width C execution for protected compiled-ROM entries, singleton VM81 admission, hidden moving-tensor route commitments, deterministic successor roots, ordered Hash72 receipts, and an authenticated persistent execution ledger.

## Current canonical path

```text
carrier correction
→ compiled Hash216 admission
→ protected native memory
→ reusable exact or parametric validation
→ persistent inventory
→ PQC checkpoint
→ RFC 3161 timestamp
→ moving tensor
→ governed projection
→ exact native-dispatch admission
→ C execution
→ successor Hash216 / Hash72
→ authenticated execution ledger
```

## Iteration 10 native operations

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

The C ABI is allocation-free, has no ambient mutable state, validates VM81/operation-slot/G243 coordinates, accepts at most eight unsigned-64 operands, and returns fixed-width deterministic results.

Native execution requires exact compatibility with the protected compiled entry, parent state, kernel policy and measurement, Hash216 lineage, trusted timestamp, moving tensor, hydration lane, compiled operand bounds, and exact read/write sets.

The physical tensor address remains internal. A Hash216 route commitment binds it to the logical address, compiled entry, and tensor closure without exposing the address.

## Governed dispatch surfaces

Capabilities:

```text
dispatch.execute
dispatch.read
```

HTTP:

```text
GET  /api/runtime/native-dispatch/status
POST /api/runtime/native-dispatch/execute
GET  /api/runtime/native-dispatch/receipts/{sequence}
```

CLI:

```text
hhs-pass213-dispatch status
hhs-pass213-dispatch execute
hhs-pass213-dispatch receipt
hhs-pass213-dispatch capability issue
```

Capability issuance remains local-only. HTTP and CLI call the same service and produce identical native results and successor commitments from identical state and request inputs.

Compilation, protected-memory reads, repair, deletion, physical map access, carrier access, RFC 3161 DER access, key access, and uncommitted state remain unexposed.

## Domains

```text
VM5184                    5,184
VM5184 × G243             1,259,712
40-lane full hydration    50,388,480
native operand width      64 bits unsigned
native max operands       8
native max results        4
```

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

Validated runtime evidence:

```text
head af36575233248d77b606ff63b41ca5e51ca23ff5
workflow run 31062363170
job 92492790661
122 tests passed
artifact pass213-iteration10-validation-31062363170
sha256:46689e6e95a99fdb1e241431809aad60d15778ea954567be22fe2de9010c3522
```

The cumulative gate builds both C libraries with warnings as errors, verifies PQC and RFC 3161 dependencies, executes all Iteration 1–10 tests, validates API/CLI parity and native execution, compiles all Python modules, parses the machine contract, and retains the transcript.

## Current boundary

Pass 213 remains draft and nonterminal. Full-hydration performance and recovery evidence, final integration, merge, and verified-main closure remain.
