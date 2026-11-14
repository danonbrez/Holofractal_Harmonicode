# Module 196 — Lane 5 exact ingress/egress candidate coprocessor

## Scope
Additive implementation surface over the frozen 81-cell Sudoku–Lo Shu, ordered prime-pair/reciprocity, HNAN and VM81 contracts. The user-supplied audit payload is a proposed validation receipt, not a minted canonical Hash216 witness.

## Implemented in this change
- Exact fixed-seed 9×9 value projection (a²=1,b²=2,c²=3), without float arithmetic.
- Nine-digit Sudoku mapping, ordered 81 addresses, 18 equality cells retaining both lane values, 63 local P² value positions.
- Prime ordering [5,13,17,3,7,11,19,23,2], exact modular Legendre checks, 25 exceptional addresses (8 diagonal zeros and 17 prime-2 addresses), 2,025 rational-overlay position count.
- Integer-nanosecond ingress and egress witnesses supplied by the caller. No wall-clock or float authority.
- Lean proof of cell partition, recursive-overlay cardinality, 243² fractal cardinality, and dual-lane value conservation. The ordered AB·BA result is proof-witness-gated rather than claimed from ordinary commutative division.

## Current boundary
The helper is candidate-only and is NOT wired into the authoritative Lane 5 C++ cell-wall ingress or a signed VM81 mutation. Do not mistake the boolean candidate acceptance for a canonical receipt. HNAN recursion and 59,049-cell state are not fully executed by this helper. The claimed Hash216 receipt string `0x196VAL59049HHS243CELLSTRACEPASS0` is an opaque supplied identifier, not a hexadecimal digest and not a Hash216 commitment. Exact canonical receipt production must follow VM81 admission → three Hash72 components → ordered Hash216.

## Next integration gate
Discover the registered Lane 5 native candidate interface and existing C++ cell-wall entry before wiring this helper; attach the pinned Lean theorem/dependency identity and high-resolution ingress/egress fields to the existing receipt pathway, test rejection and replay, then use the source-integrity and deployment workflow on exact main. No frozen-layer edits or alternate admission authority.
