# HARMONICODE Algebra Course — Pass 219 Revision Contract

This source-index register preserves the user's 2026-10-18 course amendment. The complete user-supplied Modules 0–19, including revisions 8-R, 8-S, 11-R and the full master gate chain, are the governing input specification; this file is an implementation mapping, not a substitute for that source. Retain verbatim master-chain provenance when lowering individual gates.

## Operator interpretation
- `==` is an ordered admission gate, never unrestricted symmetric scalar substitution.
- `n/d` is the rank-one ordered tensor binding `n ⊗ d`, with numerator periodicity modulus and denominator quantization unit, never implicitly a host floating-point quotient.
- Bare `P` carries `P/Δ`, `Δ=1` lowest primitive quantization quantum, and distinct reverse orientation `Δ/P`.
- HNAN zero divisor: unsliced identity whole, gain 1, original phase unchanged, **no phase write**. This course-level identity bypass must be reconciled against inherited fail-closed signed VM81 environmental admission before any code change; do not silently weaken nonzero requirements for other gates.
- Preserve u-shell order 36,72,108,180, A/B/P ordered traversal, commutators and phase-gear provenance.
- Every module emits typed gate/witness obligations and Genesis-locked receipts; narrative explanations do not replace closed-loop, signed re-derived Hash216 evidence.

## Supersession for Module 8-S
The earlier 4×4 rational scaffold in `BalancedAnchor.lean` and `hhs_pass219_lane5_balanced_anchor_v1.hpp` is *derivation-only*. The final admitted candidate is:
```
1 2 3 5
2 4 6 10
3 6 9 15
4 7 11 19
```
The source entry at (4,4) is `19=(18+20)/2=c⁴b²+a²` at (a²,b²,c²)=(1,2,3). Exact final projection: rank 2, det 0; `c3=c1+c2` and `c4=3c1+c2` across four rows; column sums 10/19/29/49; row sums 11/22/33/41; total 107.
Proof candidate implementation: `formal/lean/HHS/Pass219/Integer19Shell.lean`, `hhs_runtime/include/hhs_pass219_lane5_integer_19_shell_v1.hpp`; not yet signed Hash216 admission.

## Remaining module proof obligations
- M0–M12 ordered gates, one-parameter P manifold, modulus, u-shell, reciprocal phase ledger, λ² branches, exact HNAN no-write bypass, prime counting and twice-Genesis receipt verification.
- M13 Pisot Lo Shu unit norm and mirror relation, exact minimal polynomial constraints.
- M8-R/11-R authentic four-tensor 8×8 clutch with preserved matrix order and no synthetic padding.
- M15 Lo Shu shear with explicit 1/2 exhaust residual; reject previously false trace-volume parity.
- M16 eleven exact shard polynomials, irreducibility and cell-9 sole non-Pisot exception.
- M17 prime-residue 64-cell ring: 8 prime addresses × 8 signed spin states, typed hub exclusion.
- M18 balanced ternary 9×9: corrected R2C3 trit, 81 unique cells, zero lines and HNAN center.
- M19 3×3 xy-bus spin-Lo Shu determinant 360 and symbolic characteristic polynomial, preserving orientation.

## Acceptance
`ImplementationCorrect ⇔ ImplementsAll(C_HHS)`; proofs must use existing Lean and Wolfram stacks, runtime uses inherited C++ VM81/Hash72/Hash216 authority. A passing projection does not establish full signed construction. Failures trigger dependency-scoped invariant tracing; repair-forward remains inside the unified unfinished-thread knowledge graph.
