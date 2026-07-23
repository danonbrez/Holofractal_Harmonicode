# HHS Pass 137 — Native Proof Lifecycle Contract

## Binding pipeline

`INGRESS → GENERATION → VALIDATION → EXPANSION → COMPRESSION → STORAGE → REVERSAL → REVALIDATION → EGRESS`

A proof artifact is admitted only with byte identity, SHA-256 identity, Hash72 projection, format checks, and proof-specific validation. Compression never substitutes for proof authority. Storage is content-addressed and collision rejecting. Egress is authorized only after decompression, expansion-root verification, byte-exact reconstruction, and revalidation.

## Authority

Coq source without escape hatches is source-complete evidence, not kernel verification unless `coqc` execution is witnessed. Lean files containing `sorry` remain explicitly sketch-level evidence. Gröbner JSON is admitted only when its exact certificate reports all remainders zero.

## Invariants

1. `egress_bytes = ingress_bytes` for every artifact.
2. `decompress(compress(expansion)) = expansion` canonically.
3. Stored object identity is its compressed SHA-256 root.
4. A failed identity, parsing, proof-policy, corruption, or replay check halts the pipeline.
5. No float authority participates in proof identity or validation.
6. Compression metadata is insufficient to reconstruct authority unless the canonical proof payload and all roots are preserved.
