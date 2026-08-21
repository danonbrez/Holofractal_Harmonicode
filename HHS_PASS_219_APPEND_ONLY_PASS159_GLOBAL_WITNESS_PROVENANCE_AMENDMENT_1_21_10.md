# HHS Pass 219 — Append-Only Pass159 Whole-Expression Witness Provenance Amendment 1.21.10

## Status

`IMPLEMENTATION AUTHORIZED — ADDITIVE, NON-PROMOTING, PASS169-BOUND`

This amendment extends the validated I121.9 global constraint membrane with a deterministic provenance producer for the complete 632-byte combined Harmonicode equation.

It does not modify canonical `main`, frozen Pass159, frozen Pass169, the I121.8 source fixture, or the validated I121.9 membrane semantics.

## 1. Exact source identity

The only admitted source is:

`contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode`

with:

```text
length = 632 UTF-8 bytes
sha256 = 3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53
five `==` byte offsets = 96, 240, 266, 274, 285
```

The source remains the full combined relation. I121.10 SHALL NOT reduce it to the 348-byte numerator, cancel the repeated matrix-power denominator, replace `NcalcMatrixPower`, scalarize the `x,y,z,w` phase grammar, or substitute the denominator magnitude projection for canonical evaluation.

## 2. Whole-expression compiler provenance

The inherited Pass159 pipeline SHALL be invoked without modification:

```text
source
→ token stream
→ CST
→ AST
→ type environment
→ ordered constraint graph
→ HIR
→ VMIR
```

I121.10 records the Hash216 identity of every stage.

The already-green I121.8 census established that the full combined source differs from the numerator at every inspected stage:

```text
source_equal=0
tokens_equal=0
cst_equal=0
ast_equal=0
types_equal=0
graph_equal=0
hir_equal=0
vmir_equal=0
```

Therefore the I121.10 record is bound to genuine whole-expression compiler identity through VMIR.

## 3. Shared-environment provenance root

I121.10 MAY derive a deterministic SHA-256 provenance root from:

- a fixed I121.10 domain tag;
- exact combined-source SHA-256;
- Pass159 source/token/CST/AST/type/graph/HIR/VMIR Hash216 identities;
- the five exact UTF-8 `==` byte offsets.

This root is a shared-environment **identity binding only**. It is not:

- a scalar projection;
- an algebraic equality result;
- a Boolean gate result;
- a VM81 state root;
- a Hash72 execution receipt;
- a Hash216 transition receipt;
- a Pass169 proof;
- canonical commit authority.

The root exists so later authoritative gate witnesses can prove that all five Boolean outcomes refer to the same exact compiler-visible whole-expression environment.

## 4. Boolean truth boundary

Pass159 provenance SHALL NOT manufacture Boolean truth.

Even when all source and compiler identities are exact, the producer SHALL report:

```text
boolean_gate_results_available = false
membrane_input_ready = false
pass169_whole_expression_authority_required = true
canonical_monolithic_proof = false
```

No I121.10 function may set the five I121.9 gate results to true merely because parsing, type checking, constraint-graph construction, HIR lowering, or VMIR lowering succeeded.

Pass169 remains the inherited whole-expression authority for simultaneous constraint proof, exact symbolic validation, VM81 admission/commit, Hash72 execution evidence, Hash216 proof identity, and deterministic replay.

## 5. Authority exclusions

I121.10 SHALL expose no authority for:

```text
floating-point canonical equality
VM81 mutation
Hash72 commit
persistence mutation
canonical monolithic proof
```

The Pass159-linked producer is deliberately kept outside the cumulative exact-ABI aggregate. This prevents its Pass159/OpenSSL linkage requirements from becoming mandatory dependencies of historical exact-ABI consumers.

## 6. Required fail-closed behavior

The producer SHALL reject or fail closed when:

- source length is not exactly 632 bytes;
- source SHA-256 differs;
- the five `==` occurrences differ in count or UTF-8 byte offset;
- any required Pass159 stage fails;
- any required stage identity is unavailable;
- source-root lineage is inconsistent;
- deterministic provenance-root construction fails.

A rejected source SHALL NOT expose gate truth, membrane readiness, VM81 mutation authority, Hash72 commit authority, persistence authority, or canonical proof.

## 7. Validation gate

I121.10 is considered implementation-validated only when exact and synthetic PR lanes prove:

1. canonical lineage from frozen `main`, Pass159, Pass169, and validated I121.9;
2. frozen Pass159 and Pass169 are unchanged;
3. I121.9 membrane semantics and the exact combined source are unchanged;
4. exact source SHA and `==` offsets;
5. unchanged Pass159 build success;
6. strict C11 producer/test compilation;
7. deterministic full-stage Hash216 provenance;
8. exact source-root lineage;
9. deterministic nonzero provenance root;
10. Boolean results remain unavailable;
11. membrane input remains not ready;
12. Pass169 remains required;
13. no canonical mutation/commit authority;
14. I121.8 all-distinct source→VMIR census remains preserved.

No canonical-main merge is authorized by this amendment.
