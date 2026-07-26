# HHS Pass 159 HARMONICODE Toolchain

Contract: `HHS-P159-VM81-H216-HCI-C11C` version `1.0.0`.

This additive native C11 implementation establishes the executable Pass 159 foundation on the complete current repository nucleus. It provides:

- exact source-byte preservation and canonical source Hash216 identity;
- UTF-8 validation and a lossless token stream;
- exact CST byte round trip;
- typed AST, type-environment, constraint-graph, HIR, and VMIR artifacts;
- explicit rejection of authoritative floating-point literals;
- explicit `O != π` enforcement;
- explicit native-zero profile requirement for `1/0`;
- deterministic VM81 object and executable artifacts;
- a C11 interpreter and compiler sharing one frontend and VMIR path;
- exact interpreter/compiler semantic-root equivalence;
- Hash216 artifact lineage and Hash72 phase receipts;
- canonical binary serialization;
- replay, reverse-transition receipts, and reverse lifting;
- a versioned public C ABI and native CLI.

## Current classification

`HHS_PASS_159_FOUNDATION_IMPLEMENTED_PENDING_FULL_CLOSURE`

This classification is intentionally below the Pass 159 terminal classification. Full closure remains gated on the complete language profile, all inherited Pass 158 transition lowerings, full 159/159 positive and negative matrices, 216/216 Hash216 coverage, 81/81 VM81 coverage, sanitizer/security evidence, cross-architecture identity, and authoritative `main` closure.

## Build

```sh
make
make verify
```

Outputs:

- `dist/libhhs_pass159.so`
- `dist/libhhs_pass159.a`
- `dist/harmonicode`
- `dist/harmonicodec`
- `dist/vm81-as`
- `dist/vm81-ld`
- `dist/hhs-pass159-verify`
