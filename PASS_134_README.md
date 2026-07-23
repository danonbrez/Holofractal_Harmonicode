# Pass 134 — Recursive Full-Ancestry Checkpoint Compiler

Pass 134 implements and tests the recovery operation required after the Pass 133 wrong-parent fork.

This package is intentionally classified as a **recovery capsule**, not as a canonical full HHS checkpoint, because the authoritative full Pass 132 runtime archive is not present in the current execution environment. It preserves every available non-cache Pass 133 file and adds the complete Pass 134 compiler, tests, contracts, reports, and receipts.

## Callable surfaces

```bash
python -m hhs_runtime.checkpoint_ancestry inventory ARCHIVE.zip
python -m hhs_runtime.checkpoint_ancestry build PARENT.zip DELTA_DIR CHILD.zip --pass-id PASS_134 --parent-pass PASS_133
python -m hhs_runtime.checkpoint_ancestry recover-chain BASE.zip OPERATIONS.json OUTPUT_DIR
python -m hhs_runtime.checkpoint_ancestry locate-corruption PASS_132.zip PASS_133.zip PASS_134.zip
```

## Closure boundary

The compiler capability is verified. Historical chain closure remains blocked until the complete Pass 132 runtime checkpoint or an equivalent complete ordered operation chain is available.
