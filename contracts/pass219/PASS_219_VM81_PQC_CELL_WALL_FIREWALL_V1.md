# PASS 219 — VM81 PQC Cell-Wall Firewall v1

## 1. Purpose

This contract adds a mandatory fail-closed post-quantum admission firewall to the Pass 219 canonical VM81 boundary.

The firewall does not create a second runtime authority. It is a pre-dispatch security predicate inside the existing singleton canonical handoff.

It extends and is subordinate to:

```text
contracts/pass219/PASS_219_PLUG_AND_PLAY_MATHEMATICAL_LOGIC_SUBSTRATE_V1.md
contracts/pass219/PASS_219_PLUG_AND_PLAY_CANONICAL_HANDOFF_V1.md
contracts/pass219/PASS_219_POST_219_COMPOSITIONAL_DEVELOPMENT_ABI_V1.md
hhs_backend/runtime/hhs_pass213_pqc_enclosure_v1.py
hhs_runtime/include/hhs_pass219_rna_transcription_1_10.h
hhs_runtime/include/hhs_pass219_rna_transcription_1_10.hpp
```

Normative rule:

```text
NO instruction may reach canonical VM81 dispatch unless:
    its cell-wall path is valid,
    its inherited hash lineage is valid,
    every required Hash216 reference resolves to an authorized canonical array entry,
    and its PQC authentication verifies over the exact canonical instruction envelope.
```

The terms MUST, MUST NOT, SHALL, SHALL NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are normative.

---

## 2. Firewall location and authority

The canonical execution path becomes:

```text
Pass 220+ / external caller
        ↓ proposal only
Pass 219 substrate + RNA cell-wall lowering
        ↓ candidate + route/hash/security envelope
Pass 219 canonical handoff
        ↓
VM81 PQC cell-wall firewall
        ↓ ADMIT only
inherited singleton VM81 canonical authority
        ↓
canonical mutation + Hash72 / Hash216 lineage
```

The firewall SHALL have:

```text
instruction_admission_authority = true
canonical_mutation_authority    = false
canonical_hash72_authority      = false
canonical_hash216_authority     = false
canonical_persistence_authority = false
```

Therefore:

```text
firewall approval != canonical commit
PQC signature     != canonical receipt
valid path        != canonical receipt
Hash216 lookup    != canonical mutation
```

Only the inherited singleton VM81 authority may commit canonical state after firewall admission.

---

## 3. Canonical instruction envelope

Every instruction request that can reach canonical dispatch SHALL be represented by an exact canonical envelope `I` containing, at minimum:

```text
I = {
    domain_separator,
    pass_number,
    profile_identity,
    instruction_identity,
    exact_candidate_frame_or_digest,
    source_cell_coordinate,
    ordered_cell_wall_path,
    predecessor_hash72_reference,
    predecessor_hash216_identity,
    hash216_array_references[],
    anti_replay_sequence,
    pqc_key_identity,
    pqc_signature
}
```

The canonical domain separator for v1 SHALL be:

```text
HHS/PASS219/VM81/PQC/CELL-WALL-FIREWALL/V1
```

The signature input MUST bind the complete canonical serialization of every security-relevant envelope field except the signature bytes themselves.

No caller-controlled field may be excluded from the signed serialization if changing that field could alter routing, authority, state selection, instruction meaning, Hash216 lookup, or canonical execution outcome.

---

## 4. Cell-wall membrane path enforcement

The firewall SHALL reject any instruction whose claimed source or route does not resolve through the Pass 219 RNA cell-wall membrane.

For an ordered route:

```text
R = [c0, c1, ..., cn]
```

admission requires:

```text
cell_valid(c0)
∧ cell_valid(cn)
∧ FOR ALL adjacent (ci, ci+1): authorized_edge(ci, ci+1)
∧ reciprocal_alignment(ci, ci+1)
∧ route_orientation_valid(R)
∧ route_binds_instruction_identity(R, I)
∧ route_binds_candidate(R, I)
```

A raw pointer, foreign memory location, public API route, plugin route, GPU candidate path, cache hit, distributed-node result, or compatibility ABI symbol SHALL NOT count as a valid membrane path by itself.

An instruction originating outside the membrane may be proposed, but it MUST be lowered into a valid Pass 219 cell-wall route and then independently revalidated by the firewall before dispatch.

Any bypass, discontinuity, unknown cell, invalid edge, reversed orientation without a valid reciprocal witness, or route/candidate mismatch fails closed.

---

## 5. Hash72 lineage requirement

The firewall SHALL require the instruction envelope to bind to the inherited predecessor Hash72 lineage required by the selected canonical profile.

At minimum:

```text
hash72_reference_present(I)
∧ hash72_reference_resolves(I)
∧ hash72_reference_is_canonical(I)
∧ hash72_reference_matches_predecessor_state(I)
```

Candidate-only, local, synthetic, malformed, stale, or otherwise noncanonical Hash72 witnesses SHALL NOT satisfy this requirement.

The firewall does not create the successor Hash72. It only verifies the predecessor lineage needed to admit the instruction to canonical dispatch.

---

## 6. Hash216 array state verification

Hash216 is an execution-address and lineage boundary, not an unchecked caller-supplied label.

Every canonical instruction SHALL explicitly reference the Hash216 array entries required for its operation.

For every `r` in `I.hash216_array_references`:

```text
HASH216_REF_OK(r) :=
    reference_shape_valid(r)
∧   reference_index_in_range(r)
∧   reference_resolves(r)
∧   referenced_entry_is_canonical(r)
∧   referenced_entry_not_tombstoned(r)
∧   referenced_entry_matches_bound_identity(r)
∧   referenced_entry_matches_instruction_context(r, I)
```

Instruction admission requires:

```text
hash216_array_references_present(I)
∧ FOR ALL r IN I.hash216_array_references: HASH216_REF_OK(r)
```

The predecessor Hash216 identity SHALL also resolve to the currently authorized predecessor lineage for the requested transition.

The firewall SHALL reject:

```text
unknown Hash216 references
out-of-range references
candidate-only references presented as canonical
stale or tombstoned references
reference/value mismatches
reference/predecessor mismatches
reference/path mismatches
reference/instruction mismatches
```

A cache or vector-store entry may accelerate lookup, but cache presence alone does not establish canonical Hash216 validity.

---

## 7. PQC authentication suite

The v1 firewall SHALL inherit the existing Pass 213 PQC verifier bundle and algorithm policy rather than introducing an unrelated cryptographic authority.

The inherited suite currently defines:

```text
ML-KEM-768  = recovery / encrypted-envelope key encapsulation where required
ML-DSA-65   = operational signature authentication
SLH-DSA     = archival / independent signature authentication where required by policy
```

Canonical instruction admission SHALL require a valid operational PQC signature over the canonical instruction envelope using an authorized verifier-bundle key.

A deployment MAY require dual operational + archival signatures for higher-assurance boundaries, but a weaker local algorithm SHALL NOT silently substitute for a required PQC algorithm.

ML-KEM is not itself an instruction-authentication signature. It MAY protect confidential ingress material or recovery secrets, while admission authenticity SHALL be established by an authorized signature scheme.

PQC verification SHALL be bound to the HARMONICODE route, predecessor identities, candidate, and Hash216 references through the signed envelope. The cryptographic security claim remains the claim of the selected standardized PQC primitive; HARMONICODE phase/tensor geometry supplies execution context and domain binding rather than replacing the primitive's verification rules.

---

## 8. Anti-replay and state freshness

A valid old instruction SHALL NOT be reusable as authority for a different canonical state.

The firewall SHALL verify:

```text
anti_replay_sequence_present(I)
∧ anti_replay_sequence_expected(I)
∧ predecessor_hash216_is_current(I)
∧ instruction_not_previously_consumed(I)
```

The exact anti-replay representation MAY be a monotonic sequence, canonical transition ordinal, nonce ledger, or equivalent deterministic mechanism already governed by canonical state.

The anti-replay mechanism MUST itself be bound into the PQC-signed canonical envelope.

---

## 9. Fail-closed hard-halt semantics

Any firewall failure SHALL occur before canonical VM81 dispatch.

For every rejected instruction:

```text
canonical_vm81_dispatch = false
canonical_state_mutation = false
canonical_hash72_issue = false
canonical_hash216_issue = false
canonical_persistence = false
committed_frame = 0
```

The offending canonical execution transaction SHALL enter a fail-closed halted state.

No subsequent instruction in that transaction may execute until an explicitly authorized reset/recovery path re-establishes:

```text
valid membrane state
valid canonical predecessor lineage
valid Hash216 reference state
valid PQC verifier state
```

A malformed or hostile request SHALL NOT be permitted to partially execute and then roll back after canonical mutation. Rejection must precede dispatch.

---

## 10. Required firewall decision codes

The implementation SHALL expose distinct deterministic rejection classes at minimum equivalent to:

```text
PQC_FIREWALL_ADMIT
PQC_FIREWALL_REJECT_ENVELOPE
PQC_FIREWALL_REJECT_CELL
PQC_FIREWALL_REJECT_PATH
PQC_FIREWALL_REJECT_HASH72
PQC_FIREWALL_REJECT_HASH216_REFERENCE
PQC_FIREWALL_REJECT_PQC_KEY
PQC_FIREWALL_REJECT_PQC_SIGNATURE
PQC_FIREWALL_REJECT_REPLAY
PQC_FIREWALL_REJECT_AUTHORITY
PQC_FIREWALL_HALTED
```

The external presentation MAY map these to coarser public errors, but internal receipts/tests SHALL retain enough typed information to prove the exact rejection class.

Rejected requests SHALL NOT receive canonical Hash72 or Hash216 receipts. A separate noncanonical security audit record MAY be emitted if it cannot be confused with canonical transition authority.

---

## 11. Canonical admission predicate

Define:

```text
MEMBRANE(I) :=
    envelope_valid(I)
∧   source_cell_valid(I)
∧   ordered_cell_wall_path_valid(I)
∧   reciprocal_edge_alignment_valid(I)

HASH_LINEAGE(I) :=
    predecessor_hash72_valid(I)
∧   predecessor_hash216_valid(I)
∧   hash216_array_references_valid(I)

PQC(I) :=
    authorized_verifier_bundle(I)
∧   operational_signature_algorithm_valid(I)
∧   signature_valid_over_exact_envelope(I)

FRESH(I) :=
    anti_replay_sequence_valid(I)
∧   predecessor_is_current(I)
∧   instruction_not_consumed(I)
```

Then:

```text
VM81_PQC_FIREWALL_ADMIT(I) :=
    MEMBRANE(I)
∧   HASH_LINEAGE(I)
∧   PQC(I)
∧   FRESH(I)
∧ ¬ authority_escalation_requested(I)
```

Only when this predicate is true may the existing canonical admission authority be invoked.

---

## 12. Non-bypass law

For every callable surface `E` other than the inherited singleton canonical kernel:

```text
E may construct an instruction envelope
E may request firewall evaluation
E may observe firewall decision
E may not self-assert firewall admission
E may not bypass firewall evaluation
E may not issue canonical receipts
E may not mutate Hash216 canonical state
```

No API, ABI, plugin, compatibility symbol, direct native call, GPU path, vector-store path, distributed route, optimizer, cache, or later pass may invoke canonical VM81 dispatch without the firewall predicate.

---

## 13. Pass 220+ inheritance law

For every pass `P_n` where `n >= 220`:

```text
canonical_request(P_n)
⇒ construct_firewall_envelope(P_n)
∧ lower_through_RNA219(P_n)
∧ verify_VM81_PQC_firewall(P_n)
∧ delegate_to_singleton_kernel_on_ADMIT_only
```

No later pass may weaken, shadow, replace, or silently disable the firewall while retaining canonical compatibility.

A future successor MAY strengthen algorithms, route proofs, freshness rules, or key-management policy, but it SHALL preserve fail-closed pre-dispatch semantics and singleton canonical authority.

---

## 14. Required implementation surface

A conforming implementation SHALL add a native Pass 219 firewall surface directly in front of the canonical VM81 dispatch path.

The implementation SHALL provide, at minimum:

1. a canonical instruction-envelope type;
2. deterministic canonical serialization for PQC signing and verification;
3. cell-wall coordinate/path verification using inherited RNA/VM81 geometry;
4. predecessor Hash72 verification;
5. predecessor Hash216 verification;
6. Hash216 array-reference membership and identity validation;
7. authorized Pass 213 PQC verifier-bundle binding;
8. ML-DSA operational signature verification;
9. optional policy-gated SLH-DSA dual-signature verification;
10. anti-replay state validation;
11. fail-closed halted-state handling;
12. proof that rejection occurs before VM81 mutation, canonical receipt issuance, and persistence.

The implementation MUST NOT move canonical commit logic into the firewall.

---

## 15. Required conformance tests

A dedicated Pass 219 test SHALL prove at minimum:

```text
valid membrane path + valid Hash72 + valid Hash216 refs + valid PQC signature -> firewall ADMIT
invalid source cell -> hard reject before dispatch
invalid or discontinuous path -> hard reject before dispatch
missing predecessor Hash72 -> hard reject before dispatch
unknown Hash216 array reference -> hard reject before dispatch
out-of-range Hash216 reference -> hard reject before dispatch
stale/tombstoned Hash216 reference -> hard reject before dispatch
Hash216 reference bound to wrong instruction -> hard reject before dispatch
wrong PQC key -> hard reject before dispatch
modified signed field -> PQC signature failure
valid signature over stale predecessor -> replay/state failure
replayed consumed instruction -> hard reject
candidate attempting authority escalation -> hard reject
all rejection classes leave canonical frame/hash/persistence unchanged
firewall ADMIT still requires inherited canonical authority to commit
inherited canonical rejection after firewall ADMIT leaves no committed state
```

Tests SHALL include deterministic replay of firewall decisions and negative tests for every rejection class.

---

## 16. Closure invariant

The Pass 219 security closure is:

```text
CanonicalVM81Dispatch(I)
⇒ VM81_PQC_FIREWALL_ADMIT(I)
∧ inherited_singleton_kernel_revalidation(I)
```

and:

```text
¬VM81_PQC_FIREWALL_ADMIT(I)
⇒ HALT offending canonical transaction
∧ no VM81 dispatch
∧ no canonical mutation
∧ no canonical Hash72 issuance
∧ no canonical Hash216 issuance
∧ no canonical persistence
```

This firewall is therefore a mandatory structural admission membrane around canonical VM81 execution, not an optional network-side handshake and not an alternate canonical state machine.
