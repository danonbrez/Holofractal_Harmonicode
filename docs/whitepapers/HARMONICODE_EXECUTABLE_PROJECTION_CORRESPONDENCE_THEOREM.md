# HARMONICODE Executable Projection Correspondence Theorem

**Document class:** formal-system / implementation white paper  
**Theorem status:** implementation correspondence specification; proof requires executable evidence

## Abstract

A formal HARMONICODE rule becomes an executable-system claim only when its native typed meaning survives compilation, projection, ABI lowering, VM81 admission, and receipt generation. This paper defines the correspondence diagram and the evidence required to prove that each layer implements the same declared transition rather than a convenient approximation.

## 1. Correspondence chain

For source expression `e`, require an inspectable chain:

```text
e
→ Parse(e) = typed AST A
→ Normalize(A) = native constraint program N
→ Project(N,{pi_k}) = representation-qualified program R
→ CompileCpp(R) = C++ composition/transcription program C
→ LowerABI(C) = stable exact ABI record B
→ VM81(B,S_prev) = S_next
→ Hash72(S_prev,S_next) = transition/receipt H72
→ Hash216(previous,change,receipt) = V216.
```

## 2. Correspondence property

For each arrow `f_i`, the implementation SHALL state the preserved semantic property `I_i`.

The full chain corresponds when every stage preserves the invariants required by the final claim.

A stage may intentionally lose information only if:

1. the loss is registered;
2. no downstream claim requires the lost information; or
3. an auxiliary reconstruction witness retains it.

## 3. Executable Correspondence Theorem

### Statement

If every transformation in the lowering chain is proven semantics-preserving for invariant set `I`, and VM81 executes the exact ABI record deterministically, then the admitted VM81 successor is an implementation of the source transition with respect to `I`.

### Proof

By composition of invariant-preserving maps: if each `f_i` preserves `I`, then their composition preserves `I`. The deterministic VM81 result therefore realizes the same `I`-qualified transition as the source. QED conditional on the per-stage proof obligations.

The theorem is conditional; repository evidence must discharge each implementation premise.

## 4. Native RNA transcription

For Pass 219 RNA rules, `I` includes where applicable:

```text
ordered x,y,z,w operands
complement/orientation rule
binding/folding/gating relation
active constraint frontier
candidate delta
predecessor identity
rollback/reverse witness
Hash72/Hash216 lineage.
```

A biological name around unrelated code does not satisfy the correspondence theorem.

## 5. x86_64 boundary

The merged exact ABI supplies a byte-preserving machine projection:

```text
x86_64 ingress bytes -> exact transport -> x86_64 egress bytes.
```

Byte round-trip proves byte preservation. It does not by itself prove every native HARMONICODE semantic property unless the relevant mapping is included in the witness.

This distinction permits backwards compatibility without making x86_64 the native axiom system.

## 6. Hash72/Hash216 boundary

Hash72 is the external VM81 transition primitive, and Hash216 records the ordered three-lane transition lineage.

Therefore the executable proof object SHOULD bind:

```text
source program ID
native rule IDs
ABI bytes
VM81 predecessor/successor
Hash72 transition/receipt
Hash216 positional transition index.
```

## 7. No-float condition

A canonical correspondence proof is invalid if an authoritative stage substitutes approximate float/double/transcendental state for a symbolic/exact value without an explicitly non-authoritative projection boundary.

## 8. Indexed continuation

After Pass 218 proves optimized/reference equivalence, the source-to-execution correspondence may begin from an authenticated indexed predecessor rather than Genesis.

The predecessor witness supplies the already-proven earlier segment. New proof obligations cover the changed dependency frontier and new transition.

## 9. Negative tests

Required negative tests include:

- alter operand order `xy -> yx` and verify transition identity changes where order is active;
- erase a projection witness and require fail-closed reverse inference;
- alter one ABI field and require receipt/state mismatch;
- reorder Hash216 lanes and require identity mismatch;
- introduce float canonicalization and require rejection;
- bypass VM81 mutation authority and require rejection;
- replay from an unauthenticated predecessor and require rejection/fallback;
- map two colliding projected values back to one native state without injectivity and require rejection.

## 10. Proof artifacts

A completed Pass 219 implementation theorem SHOULD emit machine-readable artifacts sufficient to reproduce:

```text
formal source identity
type table
projection registry entries
normalized program
ABI schema/version and bytes
VM81 state roots
Hash72 receipts
Hash216 index records
test vectors
counterexample/negative-test results
benchmark evidence for performance claims.
```
