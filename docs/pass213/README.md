# Pass 213 — Iterations 1–9

Pass 213 implements an authenticated compiled ROM whose carriers are corrected before interpretation, whose canonical entries live in protected native memory, whose reusable operations receive exact or dependency-scoped admission, whose inventory survives restarts with authorized tombstones and recovery, whose checkpoints are post-quantum signed, whose history is independently timestamped, whose physical execution geometry is selected by an exact moving tensor, and whose externally visible state is limited to capability-governed public projections.

## Implemented progression

- **Iteration 1:** immutable compiled-ROM identity, integer timestamp boundaries, ordered operation chains, exact lookup, closure paths, and receipts.
- **Iteration 2:** Pass 212 correction and recovered Hash216 validation before compiled-entry decoding.
- **Iteration 3:** guarded, locked, sealed, non-executable native arenas with verified zeroization.
- **Iteration 4:** typed parametric templates, exact deltas, affected-only constraint validation, and authenticated witness reuse.
- **Iteration 5:** SQLite WAL inventory, append-only mutation roots, retained recovery carriers, tombstones, and unexplained-deletion detection.
- **Iteration 6:** ML-KEM-768 recovery, ML-DSA-65 operational signatures, SLH-DSA SHA2-128s archival signatures, protected keys, and verifier-only replay.
- **Iteration 7:** RFC 3161 external timestamp anchors bound to signed checkpoints, verifier roots, prior anchors, Hash216 lineage, local boundaries, and TSA evidence.
- **Iteration 8:** exact Lo Shu/Sudoku/Fibonacci moving tensors, reversible VM5184×G243 and full-hydration coordinate maps, exact closure proofs, Hash216 state roots, Hash72 receipts, and keyed persistent replay.
- **Iteration 9:** shared capability-governed API/CLI projection authority with append-only public commitments, source/projection receipt separation, strict protected-field rejection, and no mutation or raw-state exposure.

## Current canonical path

```text
untrusted carrier
→ Pass 212 correction
→ Hash216 compiled-ROM admission
→ sealed native memory
→ exact or dependency-scoped reuse
→ persistent inventory
→ PQC signed checkpoint
→ RFC 3161 trusted timestamp
→ exact moving tensor
→ sanitized governed projection
→ API or CLI transport
```

## Iteration 9 surfaces

Public status and catalog endpoints require no mutation authority. Protected projection lookups and verification require an exact capability scope:

```text
compiled.read
inventory.verify
tensor.read
tensor.verify
timestamp.read
integrity.verify
receipt.read
```

The HTTP and CLI transports invoke the same dispatcher and therefore produce the same governed payload, response Hash216, and Hash72 receipt. HTTP additionally applies the inherited canonical runtime response envelope.

The public projection store contains only commitments, bounded counts, invariant results, sanitized TSA metadata, and receipts. It rejects keys, tokens, authentication tags, carriers, payload bytes, native addresses, physical tensor maps, tensor seeds, recovery material, RFC 3161 DER material, and canonical floating-point values.

Compilation, execution, repair, deletion, protected-memory reads, physical tensor mapping, carrier reads, DER reads, network capability issuance, and uncommitted state remain unexposed.

## Domains

```text
VM5184                    5,184
VM5184 × G243             1,259,712
40-lane full hydration    50,388,480
axis moduli               9,9,4,4,4,3,3,3,3,3,40
```

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The dedicated workflow executes 102 cumulative tests, compiles the native and Python runtime/API/CLI modules, verifies PQC and RFC 3161 dependencies, validates FastAPI/TestClient and CLI parity, parses the Iteration 9 contract, and retains a validation artifact.

Validated implementation head:

```text
109aa45e39a33622a645a48fccb15d6101d06c38
workflow run 31058743725
job 92481849207
102 tests passed
artifact pass213-iteration9-validation-31058743725
sha256:cbb528b3e3fc4c44a8d20c39b85cead2f53298ac7390bd0ee4bb1fcb6f77cd55
```

## Current boundary

Pass 213 remains draft and nonterminal. Governed native compiled dispatch, full-hydration performance and recovery evidence, final integration, merge, and verified-main closure remain.
