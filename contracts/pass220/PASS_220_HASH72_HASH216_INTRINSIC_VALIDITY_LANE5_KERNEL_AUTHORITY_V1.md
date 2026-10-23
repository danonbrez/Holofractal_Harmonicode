# Pass 220 — Intrinsic Hash72/Hash216 validity and Lane 5 kernel-authoritative composition

Date: 2026-10-09. Applies across HHS modalities, V7 and compatible later Pass220 compositions.

## Two disjoint questions

1. **Hash state identity is intrinsic.** Every object represented in the canonical 72-symbol HARMONICODE alphabet at exactly 72 glyphs (Hash72), or as three **ordered** 72-glyph carriers of exactly 216 glyphs (Hash216), is an admissible typed hash-state object. Distinct positional provenance and Hash216 previous/change/receipt lane order survive serialization. Type checking is not a second mathematical validity proof. An arbitrary 216-character printable string with symbols **outside** the 72-letter alphabet is not a Hash216 object.
2. **Composed transitions are validated by the inherited native Lane 5/VM81 kernel.** Native phase routing, candidate-selection constraints, exact VM81 CPU equality where applicable, and existing signed environmental admission decide whether and how a composition executes. JSON `validated`, `accepted`, `candidate_only`, `probability` or `lineage_signature` metadata are neither state-validity predicates nor runtime commit grants. Descriptive JSON receipts are representations of kernel outcomes, never their source of authority.

```text
TypedHash72(H) => ValidHashState(H)
TypedHash216(H) => ValidHashState(H)
KernelAcceptLane5(C, environment) => ValidCandidateComposition(C)
CanonicalCommit(C) => ExistingSignedVM81MembraneAdmits(C)
```

Native phase/candidate ranking and `EVALUATE_PURE` do **not** mint canonical Hash72/Hash216/VM81 mutations. A complete composition/transaction must follow its real kernel and security path. Structural hash validity does not imply that a newly requested mutation is signed, replayed or admitted.

## Implementation and nonblocking search

- Removed boolean `if not candidate.validated` veto from `hhs_backend/runtime/hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.py` (earlier commit on this branch). Retained legacy field for ABI compatibility but ignored it for admission. Separate candidate identities may legally refer to the same valid Hash216 state; native ranking receives every identifier.
- Pass220 holographic bridge emits `validated=False` in legacy compatibility metadata so external JSON cannot counterfeit validation, while kernel ranking remains the real search path.
- Added native **receipt integrity** checks for the C phase-router result (prime-cell/triangular/modular/authority flags), and complete three-Hash72 vector-ranked ordinals with exact candidate source binding. A failed, incomplete or inconsistent native result is an execution failure, not a declaration that a typed Hash216 state is invalid.
- `hhs_runtime/hhs_pass220_v7_inherited_native_integration_v1.py` now limits Hash216 source, graph and VMIR glyph transport to the canonical **72-glyph alphabet**, not all printable ASCII. It never converts native 216-glyph state strings into SHA hexadecimal.
- The I002 holographic ranking layer now treats a differing prime-fingerprint profile or absent metadata as a **search-feature mismatch** (zero prime matches), not a veto on a valid Hash216 candidate. Search probability allocates optimization effort only; does not authorize canonical transitions.
- All tensor source position/ordered-phase/Lo Shu/5184 and native HNAN requirements remain intact. V7's slash operator remains delegated to inherited native type/VMIR inference.

## Focused validation contracts

Tests include: canonical glyph sets; legal duplicate hashes under different candidate IDs; legacy validated true/false produce the same kernel search; native router error dominates true JSON flag; corrupt or partial native vector-ranked source ordinals rejected; candidate foreign prime metadata merely lowers search weight; no fake commit, mutation or source mismatch accepted; original V7 Hash216 native glyph roots roundtrip without scalarization.

The regression command is `python -m pytest -q tests/pass220/test_pass220_lane5_hash216_kernel_composition_policy_v1.py tests/pass220/test_hhs_pass220_holographic_hash216_query_v1.py -k 'foreign_fingerprint_metadata_cannot_invalidate_hash216_state or native_kernel_receipt_corruption_never_counts_as_valid_composition or native_vector_receipt_requires_complete_ordered_sources or legacy_boolean_is_not_state_validity'`. Native C ABI and GPU/VM81-dependent tests are covered by `.github/workflows/pass220-lane5-intrinsic-hash-states-native-composition.yml`, compiling `make c-abi`.

Never conflate this type/metadata regression with proof that full signed VM81 and Hash72/Hash216 transitions are already executed for V7; they remain source-specific runtime evidence tasks.
