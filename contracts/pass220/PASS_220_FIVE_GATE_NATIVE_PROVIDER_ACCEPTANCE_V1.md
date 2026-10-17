# Pass 220 source-specific native proof provider acceptance

This is a source-specific adapter contract, not a proof receipt. Foreign Pass219 I162/Pass169 proofs (including five-gate proofs) cannot satisfy it.

## Inputs required before any proof promotion
- SHA-256 identity of the exact 283-byte Phase36/72 source: `ceec282499ddaf48eba1d25b6313c407d9466d379e321b47f9a6b3f752c2a499`.
- The source-derived ordered gate AST with five literal positions `54,139,223,229,276` and depths `3,3,1,0,1`, including each gate's full typed left and right operands.
- A provider-produced **verified typed algebra witness** for each gate, in order. The five gate results must not be caller Boolean declarations or a source-layout digest.
- For every gate: typed provider identity, source root, operand hashes, predecessor proof identity, native evaluation decision, exact phase-write/bypass record and signed environment attestation, with deterministic replay validation.
- VM81/Hash72/Hash216 mint only by existing authoritative runtime after all five source-specific witnesses are independently verified and the full environment admits.

## Fail-closed exclusions
- Metadata layout SHA-256 chains and Lean offset proofs are proof dependency records, not arithmetic or algebraic closure.
- The inherited I162 provider is anchored to the older 632-byte combined source; importing its verified gate mask, proof Hash216, or replay as evidence for the 283-byte source is prohibited.
- Matching five-gate counts, copied source digest, caller-defined verifier flags or the Pass159 execution-and-hold replay are insufficient.
- HNAN zero-quantization bypass is identity gain with no phase write; it does not authenticate a typed zero claim or create a mint event.

## Executable next steps
1. Extend the Pass159-to-Lane5 typed bridge to expose each complete gate operand tree and its source-locked identity without scalar evaluation or reordering.
2. Locate/adapt an actual native gate-verification provider that supports the new 283-byte source; reject unsupported source domains explicitly instead of reusing I162's five truths.
3. Bind independently verifiable provider output to source-root and predecessor lineage, and revalidate the signed environmental cell wall.
4. Exercise negative tests for foreign source identity, forged gate result, missing predecessor, zero bypass phase-write attempt, and replay mismatch.
5. Only after proof-provider execution and real VM81 admission, record runtime-generated canonical Hash72/Hash216 receipts.

## Verified prerequisite
GitHub Actions run 38895312791 for checkpoint 2406f33648d2fb6e4a15cc65332e34416ad2407f: all scoped source integrity, Python oracle, Pass159, C++ cell-wall, foreign-proof guard, HNAN, Lean and evidence-artifact steps passed.
