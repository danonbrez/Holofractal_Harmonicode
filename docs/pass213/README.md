# Pass 213 — Iterations 1–8

Pass 213 implements an authenticated compiled ROM whose carriers are corrected before interpretation, whose canonical entries live in protected native memory, whose reusable operations receive exact or dependency-scoped admission, whose inventory survives restarts with authorized tombstones and recovery, whose checkpoints are post-quantum signed, whose history is independently timestamped, and whose physical execution geometry is selected by an exact moving tensor.

## Implemented progression

- **Iteration 1:** immutable compiled-ROM identity, integer timestamp boundaries, ordered operation chains, exact lookup, closure paths, and receipts.
- **Iteration 2:** Pass 212 correction and recovered Hash216 validation before compiled-entry decoding.
- **Iteration 3:** guarded, locked, sealed, non-executable native arenas with verified zeroization.
- **Iteration 4:** typed parametric templates, exact deltas, affected-only constraint validation, and authenticated witness reuse.
- **Iteration 5:** SQLite WAL inventory, append-only mutation roots, retained recovery carriers, tombstones, and unexplained-deletion detection.
- **Iteration 6:** ML-KEM-768 recovery, ML-DSA-65 operational signatures, SLH-DSA SHA2-128s archival signatures, protected keys, and verifier-only replay.
- **Iteration 7:** RFC 3161 external timestamp anchors bound to signed checkpoints, verifier roots, prior anchors, Hash216 lineage, local boundaries, and TSA evidence.
- **Iteration 8:** exact Lo Shu/Sudoku/Fibonacci moving tensors, reversible VM5184×G243 and full-hydration coordinate maps, exact closure proofs, Hash216 state roots, Hash72 receipts, and keyed persistent replay.

## Iteration 8 canonical path

```text
trusted RFC 3161 anchor
+ signed-checkpoint root
+ verifier-bundle root
+ Hash216 lineage
+ Genesis epoch
+ tensor sequence
+ prior tensor root
+ declared domain
→ protected keyed seed
→ exact Lo Shu orientation
→ exact Sudoku tensor
→ exact Fibonacci phase
→ reversible coordinate map
→ affine full-domain closure proof
→ moving-tensor Hash216
→ canonical Hash72 receipt
→ SQLite WAL append and keyed replay
```

Canonical state uses exact integers and canonical bytes. IEEE-754 geometry is a derived, bit-committed projection and is never canonical authority.

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

The dedicated workflow runs 83 cumulative tests, compiles the native and Python runtime, verifies PQC and RFC 3161 dependencies, parses the Iteration 8 contract, and retains a validation artifact.

## Current boundary

Pass 213 remains draft and nonterminal. API/CLI parity, governed native compiled dispatch, full-hydration performance and recovery evidence, final integration, merge, and verified-main closure remain.
