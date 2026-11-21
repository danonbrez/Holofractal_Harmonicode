# Pass 220 — ChainAlpha Lane 5 Hash216 knowledge hydration (candidate)

Status: SOURCE-CLAIM CAPTURED / C++ STRUCTURAL MIRROR / LEAN KERNEL NOT YET VERIFIED / GRAPH REGEN PENDING.

## Source and scope

User-supplied `ChainAlpha.lean` is a self-contained Lean 4 (declared 4.35.0)
program of seven parts plus exact arithmetic utilities. The submission currently
appears in conversation, not as a repository source file. This contract must
not imply the complete Lean text is committed or has passed the kernel.

The text as pasted contains mojibake (e.g. `â†’`, `âˆ§`, `âŸ¨`,
`Â·`); restore exact UTF-8 Lean glyphs and compare against the authorial
source before compilation. Do not reconstruct source by guessing replacements.

## Typed candidate graph node

- kind: `FORMAL_PROOF_CANDIDATE`
- name: `ChainAlpha.main`
- source: `formal/lean/ChainAlpha.lean` (proposed; missing until committed)
- target runtime: Lean 4.35.0, core prelude
- runtime mirror: `hhs_runtime/include/hhs_pass220_chainalpha_hash216_candidate_v1.hpp`
- source provenance: submitted Lean text, source-byte hash not yet acquired
- source-status: `SOURCE_ONLY`
- proof-status: `NOT_KERNEL_VERIFIED`
- authority: `CANDIDATE_ONLY`

## Exact result (not a physical-identification claim)

```text
readout = ([(1,79), (2,48), (3,42), (6,3)], 31104)
alpha_CA = (79 + 48 sqrt(2) + 42 sqrt(3) + 3 sqrt(6)) / 31104
two-point center dimension = 3; three far ends dimension = 2
read links = 2; unread links = 1
products = 169; commutator records = 3; total records = 172
sectors:
  (+1,+1) = 79; k = 1
  (+1,-1) = 48; k = 2
  (-1,+1) = 42; k = 3
  (-1,-1) = 3;  k = 6
readout dimension = (3*2)^2 * (3*2)^2 * (3^2-1)*(2^2-1)
                  = 36 * 36 * 24 = 31104
```

The C++ mirror checks internal consistency against the stated expected result.
It does NOT compute `products`, `recs`, orthogonality, the exchange maps or
the sector counts from the original Lean definitions. A matching candidate
is not a verified Lean theorem.

## Theorem/claim relations to hydrate

1. `ChainAlpha.main` DEPENDS_ON `ChainAlpha.object_is_two_point`,
   `ChainAlpha.dressing_of_the_qutrit_qubit_link`, the exact Part 0/1 definitions
   and the kernel's reduction machinery.
2. `ChainAlpha.dressing_of_the_qutrit_qubit_link` HAS_EXACT_READOUT the ordered
   radical coefficient/radicand pairs and denominator above.
3. `ChainAlpha.records_orthogonal` STATES_ORTHOGONALITY of 172
   non-null record directions under the defined pairing.
4. `ChainAlpha.sectors` HAS_EXCHANGE_SECTOR each ordered (X,Y) pair above.
5. `ChainAlpha.selection_under_read_cap` IS_CONDITIONAL_ON
   `ReadCap Readable`; unlike `ChainAlpha.main`, its hypothesis is explicit.
6. `ChainAlpha.readers_reproduce_the_cap` derives the internally
   defined `readableByReads` predicate; it is not a kernel proof of the
   external mathematical literature.
7. `ChainAlpha.configuration_unique` is conditional on its listed world,
   two-point, read-end, readability and acting-charge hypotheses.
8. `ChainAlpha.commutant_dimension`, `ChainAlpha.action_rank`,
   `ChainAlpha.commutator_records`, `ChainAlpha.exchanges_agree_with_pairings`
   are distinct theorem nodes, not additional assumptions of `main`.
9. `ChainAlpha.join_probability` is an exact finite ket computation with
   the interpretation noted in the original commentary.

## Verified-identity admission requirements

Follow the inherited Pass 219 Lane 5 1.69 graph/database generator and
Pass 220 I051 native Lean proof-receipt machinery, rather than introducing
a new independent hash or knowledge-store authority.

Required before promotion of this candidate:
1. Commit exact normalized source bytes as a distinct formal source,
   preserving operator order and proof/definition boundaries.
2. Pin the Lean 4 toolchain and run `lean ChainAlpha.lean`; capture version,
   exit code, stdout/stderr and compiler/kernel proof diagnostics.
3. Run all `#print axioms` checks. Preserve the distinction between
   computational kernel proof and any dependencies/hypotheses in selection.
4. Generate the inherited theorem and dependency identity; link the original
   source-byte identity, exact result, checked theorem IDs, and validation
   receipts through the existing Hash72/Hash216 contract.
5. Regenerate the repository Hash216 dependency index and Lane 5 1.69
   knowledge projection; hydrate its existing SQLite tables and verify
   receipt/replay deterministically.
6. Pass the guarded Pass 219 C++ RNA cell wall and applicable Lane 5
   constructor contracts before any later admission action.

No automatic equivalence to a physical constant, no inference about full
unitary groups, and no canonical mutation/Hash72 mint/Hash216 mint/persistence
authority are granted by this candidate.
