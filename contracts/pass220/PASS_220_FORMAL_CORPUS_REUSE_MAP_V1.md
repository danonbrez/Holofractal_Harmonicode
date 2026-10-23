# Pass 220 Formal Corpus Reuse Map

Source of record: https://github.com/danonbrez/Holofractal_Harmonicode/tree/main/formal

## Existing verified source locations to inherit (without promoting beyond their claims)
- `formal/lean/HHS/Pass220/HNANPhase5184.lean`: ordered three-by-three HNAN roles and cells; noncommuting phase labels; 5184 factorization; raw-frame round-trip; authorityFailClosed. Local Lean theorem bodies are visible in the source; this mapping does not claim we ran Lake.
- `formal/lean/HHS/Pass219/QGUHNANTransport.lean`: Pass219 transport lane. Inspect the precise theorem signatures before reuse.
- `formal/lean/HHS/Mathlib/Rat/Congruence.lean`: exact rational addition/multiplication congruence under explicitly scoped conventional Int commutations. The module explicitly sets `genericHHSCommutationAuthorized := false` and defers quotient construction. Do not reuse those commutations as unrestricted ordered phase laws.
- `formal/lean/HHS/Mathlib/Rat/Value.lean` and `ValueAlgebra.lean`: exact-value constructors; verify local prerequisites before proof import.
- `formal/lean/HHS/Alignment/ReciprocalTensor.lean`: candidate locus for ordered reciprocal tensor alignment; inspect declarations and admission scope.
- `formal/wolfram/pass219_ordered_constraint_formalization_1_0.wl`: Wolfram ordered-gate bridge.
- `formal/lemmas/pass_144/LEMMA_CORPUS.json`: established lemma substrate, separate from live signed VM81 receipts.
- `formal/coq/HHS_GFE_Field_Quotient.v` and `formal/certificates/gfe_state_5_4_grobner.json`: additional evidence types, not automatic validation of new 283-byte gate semantics.

## Implementation rules for PR #806
1. Reuse already-declared Lean/Coq/Wolfram proof identities; avoid creating a parallel algebra that changes operand order or typed-zero meaning.
2. Bind every imported theorem by explicit module, theorem name, source SHA/tree provenance and checker output before calling it verified for this particular source.
3. Existing formal theorems for HNAN orientation, raw round-trip, or integer congruence do not establish five-gate source-specific semantic closure.
4. `hhs_pass220_rank1_hnan_v1.hpp` remains a candidate-only C++ boundary until an actual trusted typed-zero witness is bound; the formal corpus can help prove its invariant but cannot mint VM81 Hash72/Hash216.
5. Require source-gate identities, predecessor linkage, exact phase record, signed environment and admitted VM81 replay before any canonical-closure claim.
6. The Lake root is `lakefile.lean` with `srcDir := "formal/lean"`; the repository uses one native Lean package, not an external mirror.

## Validation and next work
- This file is a discovery/reuse map, not a proof certificate.
- Inspection performed through GitHub connector of index, HNANPhase5184.lean, Rat/Congruence.lean and lakefile.lean. No Lean, Coq, Wolfram or VM81 command was executed for this checkpoint.
- Next bounded step: inspect HNAN transport and ReciprocalTensor theorem signatures; add a source-specific Lean proof statement that imports established lemmas, then validate through pinned Lake build. Integrate proof identity into the existing VM81 authority chain only after checker-backed success.
