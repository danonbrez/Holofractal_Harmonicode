# Next Pass — Pass 077

## Harmonicode Compiler and Artifact Lineage Pipeline

Pass 077 should compile committed, validated typed IR or executable IR into a deterministic target artifact while preserving:

- source and typed-IR lineage;
- exact types and source spans;
- invariant bindings;
- effect declarations and authority requirements;
- optimization proofs;
- target-independent intermediate representation;
- compilation receipts;
- reproducible artifact roots;
- non-self-authorizing compiled outputs.

The compiler must use the Pass 074 unified Runtime API, consume Pass 075 typed IR, and reuse Pass 076 execution tests as semantic equivalence checks. The Pass 072 foundation remains unchanged.
