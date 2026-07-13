# Integration Report — Pass 016

Pass 016 moves the next authority boundary outward from the ledger into the canonical runtime surfaces that create payload hashes.

Before this pass, the unified ledger was already kernel-backed, but IO, semantic-memory, and runtime-contract payload hashes could still be projected through a parallel helper. That did not bypass the ledger, but it left duplicate Hash72 projection semantics at important propagation surfaces.

This pass unifies those surfaces under the C `u^72` Digital DNA kernel witness path:

```text
payload / semantic record / runtime contract
→ canonical JSON projection
→ C u^72 Digital DNA transport
→ 72-symbol digest
→ full kernel witness surfaced on record
```

The engineering intent is not to replace the ring with a static digest. The digest is now a projection of the kernel witness, while the witness carries the DNA, rotation profile, trace count, positions, and zero-sum closure status.

## Boundaries unified

- Canonical IO gateway
- Validated vector-cache write guard
- Semantic memory guard
- Canonical runtime contract payload hashes
- API/runtime packet contract hashes indirectly through runtime contract helpers

## Remaining migration surface

Pass 017 should continue this outward migration into:

- runtime dataflow/event guard surfaces,
- persistence contract projections,
- high-risk legacy modules that still import `hhs_loshu_phase_embedding_v1.hash72_digest`,
- GUI-facing packet adapters.
