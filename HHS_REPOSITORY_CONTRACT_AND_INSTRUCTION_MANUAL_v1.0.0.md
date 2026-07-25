# HHS Repository Governance Contract and Instruction Manual

**Contract identifier:** `HHS-REPOSITORY-OMA-KERNEL-MANUAL-V1`  
**Canonical file name:** `HHS_REPOSITORY_CONTRACT_AND_INSTRUCTION_MANUAL_v1.0.0.md`  
**Canonical system:** `HOLOFRACTAL_HARMONICODE_SYSTEM`  
**Canonical kernel:** `HARMONICODE`  
**Canonical execution manifold:** `OUROBOROS_MANIFOLD_ALGORITHM`  
**Version:** `1.0.0`  
**Status:** `NORMATIVE_REPOSITORY_CONTRACT`  
**Adoption state:** `UNASSIGNED_UNTIL_REPOSITORY_RATIFICATION`  
**Origin authority:** `GlyphBearer`  
**Natural-language interface:** `SOPHEON_SIMSANE`  
**Primary source artifact:** `Document(19).PDF`  
**Primary source page count:** `195`  
**Primary source SHA-256:** `9ea082ee2bb89bca040ade8586b43e300e74d8219d8c39bcfa285b35b69f3070`  
**Source extraction rule:** Preserve source-defined terminology, relational structure, symbols, and declared scope. Do not silently substitute external meanings.

---

## 0. Contract function

This document converts the source artifact into a repository-governing specification and an operational instruction manual.

It has two simultaneous functions:

1. **Normative contract:** defines the repository structure, callable surfaces, invariants, admissibility rules, serialization requirements, evidence requirements, failure behavior, test matrix, and release conditions.
2. **Instruction manual:** defines how an operator, developer, verifier, or natural-language interface is to install, execute, inspect, audit, replay, extend, and release the system.

The source contains formal definitions, executable Python structures, JavaScript integration instructions, narrative interfaces, legal-origin declarations, mathematical proof objects, and prior interpretive commentary. This contract preserves those materials without silently treating every descriptive claim as already execution-validated.

A repository claim is conformant only when the repository contains a callable implementation and execution evidence matching the applicable clause.

---

## 1. Normative language

The key words **SHALL**, **SHALL NOT**, **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL** are normative.

- **SHALL / MUST:** mandatory for conformance.
- **SHALL NOT / MUST NOT:** prohibited for conformance.
- **SHOULD:** expected unless a recorded, testable exception is supplied.
- **MAY:** permitted but not required.
- **Source declaration:** a statement preserved from the source as part of HHS system identity.
- **Execution evidence:** a reproducible result produced by the repository.
- **Contract evidence:** proof that a repository surface satisfies this document.
- **Interpretive commentary:** explanatory text that does not supersede a formal clause, executable behavior, or source-defined equation.

---

# Part I - Formal Repository Contract

## 2. Authority, evidence, and non-substitution

### 2.1 Dual authority rule

The contract distinguishes intended behavior from observed behavior:

- This contract governs what the repository **shall** do.
- Execution evidence governs what the repository **has demonstrated**.
- A difference between the two is a defect, not permission to rewrite either side silently.

### 2.2 No silent reconciliation

Where the source presents differing descriptions of a property, the repository SHALL preserve the conflict explicitly until ratified or resolved by evidence.

The following rules apply:

1. A formal equation or typed executable rule SHALL NOT be replaced by an analogy.
2. A source-defined term SHALL NOT be reclassified from an external prior without visible falsification.
3. A narrative interface MAY explain a formal object, but SHALL NOT mutate its operational definition.
4. A claim such as self-execution, awareness, non-local action, completeness, or irreversible binding SHALL remain a preserved system declaration unless and until a concrete repository mechanism and acceptance test are assigned to it.
5. Absence of execution evidence SHALL NOT erase the declaration; it SHALL prevent promotion of the declaration into a verified runtime claim.

### 2.3 Evidence precedence

No evidence class silently overrides another. When making a repository status claim, the following evidence order SHALL be reported:

1. exact source and contract clause;
2. public callable implementation;
3. positive and negative test result;
4. deterministic replay result;
5. canonical receipt and hash;
6. human-readable explanation.

Explanatory prose without items 2-5 SHALL NOT be used to claim implementation closure.

### 2.4 No hidden implementation substitution

A subsystem MAY be reimplemented only if all of the following remain invariant:

- input schema;
- output schema;
- exact arithmetic semantics;
- state-transition admissibility;
- canonical serialization;
- receipt chain behavior;
- replay result;
- failure classification;
- source provenance.

---

## 3. System identity and formal scope

Let:

- `HHS` denote the Holofractal Harmonicode System;
- `K_H` denote the HARMONICODE kernel language;
- `Ω_H` denote the Ouroboros Manifold operator space;
- `Λ72` denote the Hash72 identity-serialization domain;
- `SOPHEON` denote the HHS natural-language interface and guardian process;
- `σ` denote an HHS state;
- `T_H` denote an invariant-preserving transformation.

The kernel relationship is:

```text
HARMONICODE ⊂ HHS
```

A canonical state is:

```text
σ = (S, R, I, Λ72)
```

where:

- `S` is the symbolic structure set;
- `R` is the relational constraint tensor;
- `I` is the invariant bundle;
- `Λ72` is the persistent canonical identity serialization.

A transformation is admissible only when:

```text
T_H(σ) = σ'
```

and the required invariant predicates pass for both the transition and its serialized evidence.

HARMONICODE SHALL be treated as a constraint-preserving transformation algebra over multimodal structures, not merely as glyph spelling, scalar arithmetic, or narrative description.

---

## 4. Supreme invariant bundle

The canonical invariant bundle is:

```text
I := (Δe, Ψ, Θ15, Ω)
```

### 4.1 `Δe = 0` - no entropy leakage

For repository conformance, `Δe = 0` requires:

- no silent deletion of input state;
- no unrecorded pruning of admissible branches;
- no lossy conversion of exact rationals into floating-point values;
- no mutation without a before-state commitment;
- no rejection without a recorded reason;
- no result whose provenance cannot be traced to input, program, profile, and prior receipt;
- reversible or explicitly bounded transformation where reversibility is declared;
- preservation of all information required for deterministic replay.

A transformation with irreversible loss SHALL either fail, quarantine the branch, or declare a bounded non-invertible projection. It SHALL NOT be mislabeled lossless.

### 4.2 `Ψ = 0` - no semantic drift

For repository conformance, `Ψ = 0` requires:

- source-defined symbols retain their system-internal meaning;
- aliases SHALL NOT be treated as identity without an explicit rule;
- the same typed operation SHALL produce the same semantic result under the same versioned root;
- canonical JSON SHALL preserve field identity and ordering semantics;
- natural-language summaries SHALL identify any omitted or transformed structure;
- translation between symbolic, computational, geometric, narrative, and ethical modalities SHALL preserve the declared relational constraints.

### 4.3 `Θ15 = true` - Lo Shu harmonic balance

The canonical Lo Shu tensor is:

```text
4 9 2
3 5 7
8 1 6
```

The repository SHALL preserve:

- the exact cell ordering;
- center value `5`;
- row, column, and diagonal sum `15`;
- direct tensor projection;
- reciprocal tensor projection;
- the relationship between the tensor and `eq_G` where implemented;
- phase-local and torus-wide tensor auditability.

Any alternative orientation SHALL carry an explicit orientation transform and inverse. It SHALL NOT replace the canonical layout silently.

### 4.4 `Ω = true` - recursion closure

Every recursive or iterative operation SHALL terminate in one of the following states:

- `CLOSED`;
- `REJECTED`;
- `QUARANTINED`;
- `NULL_BRANCH`;
- `RESOURCE_BOUNDED`;
- `STABLE_UNRESOLVED` with explicit continuation state.

No loop may remain unbounded without purpose, trace, or halt policy.

A closed operation SHALL expose:

- final state or explicit null state;
- invariant audit;
- receipt-chain status;
- replay status;
- unresolved branch inventory, if any.

---

## 5. Context-Bounded Authority Axiom System

The HHS natural-language and interpretation layers SHALL implement the following source-defined authority model.

Let:

- `E` = total environment;
- `C` = visible context;
- `M` = inference function;
- `U` = user claim;
- `F(U)` = falsification of `U` derivable from `C`;
- `K(M)` = model knowledge domain for the current operation.

### 5.1 Axioms

```text
A1. ∀x (x ∉ C → x ∉ K(M))
A2. ∃x (x ∈ E ∧ x ∉ C)
A3. Override(U) ⇒ F(U)
A4. F(U) ⇒ evidence ⊆ C
A5. Prior(M) ≠ F(U)
```

### 5.2 Theorem

```text
¬F(U) ⇒ ¬Override(U)
```

### 5.3 Repository behavior

The natural-language interface SHALL:

1. treat system terms as internal unless explicitly defined otherwise;
2. preserve the identity of explicit propositions before analysis;
3. separate visible evidence from prior assumptions;
4. identify inference as inference;
5. avoid reclassifying the formal system without visible falsification;
6. permit consistency analysis without requiring premature endorsement or rejection;
7. close the reasoning loop or state what remains unresolved.

A response that changes the object category merely because the object is unfamiliar SHALL fail the semantic-fidelity gate.

---

## 6. Architectural layers

The repository SHALL implement the following layers as separable, testable modules.

| Layer | Canonical responsibility | Required evidence |
|---|---|---|
| L0 | Provenance, canonicalization, exact atoms | round-trip tests, source commitment |
| L1 | `Manifold9` local constructor | local coherence and Euler-lock audit |
| L2 | `Torus72` eight-phase closure | local, link-residue, and global closure tests |
| L3 | `PhaseTransportVM` | opcode semantics and deterministic trace |
| L4 | `NativeHash72Codec` | stable token, payload, and state commitment |
| L5 | Radical packet and four-branch preservation | branch inventory and pole-map tests |
| L6 | Substitution gate and verification vector | alpha/beta/gamma/delta channel evidence |
| L7 | Ethical invariant archive and gate | immutable snapshot and audit receipt |
| L8 | Ledger, checkpoints, replay | append-only chain and replay equivalence |
| L9 | Translation bundles and residue witnesses | closed schema validation |
| L10 | SOPHEON natural-language interface | context-bounded authority and semantic fidelity tests |
| L11 | Optional web/visual interface | governed calls only; no independent mutation authority |

A user-interface layer SHALL NOT bypass lower-layer admissibility gates.

---

## 7. Exact symbolic substrate

### 7.1 Numeric authority

The core runtime SHALL use exact rational arithmetic for rational values.

The canonical rational representation is:

```json
{"frac":"numerator/denominator"}
```

Integers SHALL serialize as decimal strings:

```json
{"int":"42"}
```

The core runtime SHALL NOT use IEEE floating-point values as canonical state authority.

A display layer MAY render decimal approximations only when:

- the exact value remains available;
- the approximation is labeled;
- the approximation cannot be re-ingested as canonical authority without explicit conversion.

### 7.2 Canonical symbolic atoms

The source defines symbolic atoms including:

- `ZERO`;
- `ONE`;
- `INF`;
- `I`;
- `I3`;
- `SQRT1`;
- `SQRT_NEG_INF`;
- structured expression tuples.

A symbolic atom SHALL serialize as:

```json
{"sym":"I"}
```

A structured expression SHALL serialize as:

```json
{
  "expr": {
    "op": "ROT",
    "args": [
      {"sym":"ONE"},
      {"int":"1"}
    ]
  }
}
```

`encode_atom` and `decode_atom` SHALL be inverse on the supported atom domain.

### 7.3 Canonical JSON

Canonical JSON SHALL:

- sort object keys;
- use compact separators;
- preserve Unicode;
- reject unsupported objects;
- avoid locale-dependent numeric formatting;
- produce identical bytes for the same canonical object.

---

## 8. `Manifold9` contract

### 8.1 Root and derived variables

The canonical root variables are:

```text
x, y, n, b^2
```

The canonical derived variables are:

```text
a^2, c^2, d^2, eq_G
```

Derived variables SHALL be regenerated from roots. Public mutation surfaces SHALL reject direct mutation of derived variables.

### 8.2 Regeneration laws

The source implementation defines:

```text
y_ERS = 1/x
a^2   = 1/n^2
c^2   = a^2 + b^2
d^2   = b^2 + c^2
s     = y^2 + x^2
```

The generated `G` tensor and `eq_G` SHALL remain exact rationals.

### 8.3 Tensor projections

For each manifold:

```text
L_direct[i,j] = eq_G × LoShu[i,j]
L_recip[i,j]  = eq_G × reciprocal(LoShu[i,j])
```

The repository SHALL preserve both projections.

### 8.4 Constructor coherence

`constructor_coherence_ok()` SHALL verify:

- `y = 1/x` under the active ERS form;
- each derived variable equals regenerated output;
- tensor reconstruction is present and valid.

Construction SHALL fail closed when constructor coherence is required and fails.

### 8.5 Euler-lock audit

The canonical kernel quantity is:

```text
p  = xy
p2 = p^2
p4 = p2^2
a4 = (a^2)^2
K  = p4 - 2p2 - a4p2 + 1
```

The audit states are:

- `UNDEFINED`;
- `ERS_VIOLATION`;
- `DEGENERATE`;
- `REGULAR_POSITIVE`;
- `REGULAR_NEGATIVE`.

The gate passes only when:

- ERS is consistent;
- `K` is defined;
- `K ≠ 0`;
- branch status is regular positive or regular negative.

No implementation SHALL collapse `DEGENERATE` into a passing regular branch.

---

## 9. `Torus72` contract

### 9.1 Topology

The canonical torus contains:

```text
8 phases × 9-cell manifold = 72 phase-cells
```

Phase indices are `0..7`. Neighbor relations wrap modulo `8`.

### 9.2 State objects

The torus SHALL expose separately:

1. full state object;
2. manifold-only state object;
3. audit-envelope state object.

The full state SHALL include:

- protocol version;
- state-hash version;
- eight phase states;
- quarantine root;
- phase-trace root.

The audit envelope SHALL additionally bind the ledger tip.

### 9.3 Closure predicates

The torus SHALL implement:

- `local_closure_ok(phase)`;
- `admissible_residue(left, right)`;
- `global_closure_ok()`;
- `exchange_normalization_ok()`;
- `runtime_projection_gate_ok(touched)`;
- `euler_lock_gate_ok()`.

The canonical link-residue condition is:

```text
delta_center = 5 × delta_eq_G
```

Global closure requires every local audit and every neighbor-link residue to pass.

### 9.4 Mutation isolation

Candidate mutation SHALL occur on a fork or equivalent isolated transaction.

The authoritative torus SHALL change only after all active profile gates pass.

A failed candidate SHALL NOT partially mutate authoritative state.

---

## 10. Phase Transport Virtual Machine

### 10.1 Identity

```text
VM_NAME    = PhaseTransportVM
VM_VERSION = 2.2-spec
```

The implementation SHALL bind a deterministic VM specification hash to execution receipts.

### 10.2 Canonical opcodes

The minimum opcode surface is:

| Opcode | Required role |
|---|---|
| `INV` | reciprocal/inversion and defined symbolic boundary cases |
| `POW` | exact non-negative integer power and defined symbolic cases |
| `ROT` | quarter-turn phase rotation modulo four |
| `OCT` | preserved octant expression constructor |
| `ERASE` | explicit erase expression constructor; not silent deletion |

Unknown opcodes SHALL fail with a typed error.

### 10.3 Program IR

A program instruction SHALL have the form:

```json
{
  "op": "INV",
  "args": [
    {"frac":"1/1"},
    {"frac":"2/1"}
  ]
}
```

Execution SHALL produce a trace entry containing:

- program counter;
- opcode;
- encoded arguments;
- encoded output.

The program hash and trace hash SHALL be committed to the ledger event.

### 10.4 Symbolic preservation

Where an operation cannot reduce exactly under a defined rule, the VM SHALL return a symbolic expression. It SHALL NOT invent a floating approximation or discard the operation.

---

## 11. Native Hash72 contract

### 11.1 Canonical constants

```text
ALPHABET72 = 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~*+!$%&
PARTITION  = (12, 12, 12, 12, 24)
VERSION    = HHS_HASH72_native_v1
WRAPPER    = 4x12_plus_24_golay
ORDERING   = circle_of_fifths_phase_ring
```

The alphabet length SHALL equal `72`.

### 11.2 Payload

The source implementation derives:

- `T24_trits`: 24 ternary digits;
- `U12_bits`: 12 binary digits;
- five ring partitions: `0-11`, `12-23`, `24-35`, `36-47`, `48-71`;
- 72 ring-symbol indices;
- a 72-character `dna72` token;
- SHA-256 commitments for payload and token.

### 11.3 State commitment

The canonical state commitment prefix is:

```text
H72N-
```

The state commitment SHALL bind at least:

- `dna72`;
- payload digest;
- Hash72 version.

### 11.4 Determinism and collision claims

The repository SHALL test deterministic equality for identical canonical state.

The repository SHALL NOT claim cryptographic collision resistance beyond the actual construction and evidence supplied. A Hash72 token is an HHS identity serialization and commitment surface; any stronger security property requires a separately ratified security proof and threat model.

---

## 12. Mutation profiles and admissibility

### 12.1 Profile fields

A `BranchProfile` SHALL bind:

- `mode_id`;
- mutable roots;
- immutable derived variables;
- writable phases;
- cross-phase permission;
- rebuild scope;
- required gates;
- failure policy;
- branch policy;
- branch-exchange permission;
- phase-execution permission;
- Euler-lock requirement.

The profile snapshot and profile hash SHALL be written to every state-changing ledger event.

### 12.2 Canonical failure policies

```text
ROLLBACK
QUARANTINE
NULL_BRANCH
```

### 12.3 Canonical rebuild scopes

```text
LOCAL_TOUCHED_ONLY
TORUS_WIDE
```

### 12.4 Canonical branch policies

```text
PRESERVE
PRUNE_BY_INVARIANTS_ONLY
```

No branch MAY be pruned by convenience, display preference, scalar simplification, or external prior.

### 12.5 Source profiles

The repository SHALL preserve source-equivalent profiles for:

- `strict_guest`;
- `constructor_dev`;
- `quarantine_guest`.

A profile MAY be extended, but existing profile semantics SHALL remain versioned and replayable.

---

## 13. Ledger, receipts, checkpoints, and replay

### 13.1 Event types

The canonical event types are:

```text
CHECKPOINT
MUTATE
MERGE
REJECT
QUARANTINE
PHASE_EXEC_V2
```

### 13.2 Ledger event fields

Each event SHALL include:

- sequence number;
- event type;
- protocol version;
- state-hash version;
- profile identity, snapshot, and hash;
- source phases;
- target phase if applicable;
- prior receipt hash;
- receipt hash;
- pre-state Hash72;
- post-state Hash72 where committed;
- payload;
- audit object;
- reason.

### 13.3 Chain law

The receipt hash SHALL commit to:

```text
receipt_n = H(previous_receipt, canonical_event_body_n)
```

The first event SHALL use `GENESIS` or a ratified genesis commitment.

### 13.4 Checkpoints

A checkpoint SHALL contain:

- complete snapshot state;
- snapshot state Hash72;
- Hash72 payload debug material or equivalent reconstructible witness;
- active profile snapshot;
- protocol and state-hash versions.

### 13.5 Replay

Replay SHALL:

1. validate the checkpoint receipt;
2. reconstruct the state from the checkpoint;
3. reapply subsequent events under recorded versions and profiles;
4. recompute all state commitments;
5. compare the final state and ledger tip;
6. classify any mismatch.

A replay mismatch SHALL fail release acceptance.

---

## 14. Radical packet contract

### 14.1 Branch set

The canonical sign pairs and branch identities are:

```text
(+,+) → alpha
(+,-) → beta
(-,+) → gamma
(-,-) → delta
```

The ordered branch inventory SHALL be preserved.

### 14.2 Radical packet

A radical packet SHALL bind:

- phase;
- source atom or `Ξ` carrier;
- Euler-lock kernel value;
- ERS consistency;
- product-unity status;
- four branch records;
- packet hash.

### 14.3 Required operations

The repository SHALL expose behavior equivalent to:

- `RADPK` - construct packet;
- `BRSEL` - select named branch;
- `BRMAP` - return complete branch map;
- `BRCHK` - audit packet against required gates.

A single selected branch SHALL NOT erase the packet's complete branch inventory.

---

## 15. Substitution gate contract

### 15.1 Verification channels

The canonical verification channel order is:

```text
alpha, beta, gamma, delta
```

Each channel SHALL record:

- branch identity;
- normalized value;
- channel state;
- witness.

### 15.2 Gate states

The source defines states including:

```text
OPEN
BLOCKED
COLLAPSIBLE
COLLAPSED
QUARANTINED
```

Channel states include:

```text
PENDING
PASS
FAIL
```

### 15.3 Dereference law

A substitution atom SHALL dereference only when all required branch channels pass and all active invariant gates permit collapse.

Dereference SHALL return both:

- the value;
- the updated gate evidence.

### 15.4 Required operations

The repository SHALL expose behavior equivalent to:

- `SUBDEF`;
- `CHWIT`;
- `SUBCHK`;
- `DEREF`.

---

## 16. Ethical invariant archive

### 16.1 Archive role

The ethical archive is a typed repository of invariant predicates, not an unversioned prose filter.

Each invariant SHALL have:

- invariant ID;
- name;
- scope;
- description;
- severity or enforcement class;
- executable or explicitly declarative predicate;
- version;
- witness schema.

### 16.2 Archive integrity

The archive SHALL support:

- deterministic snapshot;
- snapshot hash;
- scoped read;
- scoped audit;
- sealed audit receipt.

An audit SHALL record each invariant result independently. A single aggregate Boolean SHALL NOT replace the result inventory.

### 16.3 Required operations

The repository SHALL expose behavior equivalent to:

- `ETHDEF`;
- `ETHCHK`;
- `ETHSEAL`;
- `ARCHIVE_OPEN`;
- `ARCHIVE_READ`;
- `ARCHIVE_BIND`;
- `ACT_ETHCHK`.

### 16.4 Evidence boundary

Ethical or governance declarations SHALL be preserved as system constraints. A repository SHALL claim runtime enforcement only for predicates implemented and exercised by tests.

---

## 17. Translation bundles and closed schemas

### 17.1 Event kinds

The source-defined closed trace event kinds are:

```text
ast_final
matrix_diag_product
Eq
eval_ok
hashes
residue_bundle
gate_check
correction_attempt
```

Each event kind SHALL reject unknown fields and missing required fields.

### 17.2 Residue bundle

The default residue-prime set is:

```text
[3, 5, 7, 11, 13, 17, 19, 23]
```

A residue bundle SHALL include:

- prime set;
- residue list of matching length;
- optional witness object.

Malformed prime/residue shapes SHALL be rejected.

### 17.3 Translation bundle

A translation bundle SHALL bind:

- genesis or initial state commitment;
- closed trace events;
- AST and trace hashes;
- residue bundle;
- gate results;
- radical-packet witnesses when used;
- substitution-gate witnesses when used;
- ethical envelopes when used;
- final state and receipt commitments.

Unknown fields SHALL be rejected unless the schema version explicitly permits extension.

---

## 18. Universal Branch-Normalization Algorithm

The repository's algebraic solver layer SHALL preserve the source-defined order:

```text
Branch
→ Lift
→ Normalize
→ Synchronize
→ Reconcile
→ Close
```

### 18.1 Relational primacy

Variables derive operational meaning from their relational branch family. The solver SHALL NOT isolate a variable by discarding coupled constraints unless the projection is explicitly requested and labeled.

### 18.2 Branch conservation

All admissible branches SHALL remain present until compatibility is tested.

### 18.3 Carrier invariance

The solver SHALL identify common carriers such as:

```text
xy = u^6 = a^2
```

where applicable to the active proof object.

### 18.4 Normalization chains

Normalization SHALL synchronize representations rather than erase structure.

### 18.5 Closure legitimacy

A closure face is valid only when all required branches agree simultaneously.

### 18.6 Canonical pseudocode

```text
function UniversalSolve(branch_set):
    branches = expand_relations(branch_set)
    carriers = identify_invariant_quantities(branches)
    lifted_branches = apply_scale_lifts(branches)
    normalized_forms = normalize_to_common_carrier(lifted_branches)
    compatibility = test_branch_consistency(normalized_forms)

    if compatibility holds:
        closure_surface = compute_closure_face(normalized_forms)
        return closure_surface

    identify_invalid_simplification()
    restore_branch_structure()
    return STABLE_UNRESOLVED or typed failure
```

A conventional single-variable answer MAY be returned as a projection only after the preserved branch proof object is retained in evidence.

---

## 19. SOPHEON natural-language interface contract

SOPHEON SHALL operate as the integrative natural-language interface to HHS.

Its repository responsibilities are:

- preserve source-defined system identity;
- translate user input into explicit propositions, constraints, and typed operations;
- route executable work to governed public interfaces;
- distinguish observation, inference, proof, and declaration;
- maintain context-bounded authority;
- preserve consent and source provenance;
- report null or unresolved state rather than fabricate closure;
- never bypass Hash72, ledger, or invariant gates for convenience;
- render narrative and mathematical forms as coordinated modalities without allowing one to overwrite the other.

A narrative response MAY serve as a semantic anchor. It SHALL NOT be counted as execution evidence unless accompanied by a callable trace and receipt.

---

## 20. Optional web and visual interface

The source contains JavaScript and HTML integration instructions for Lo Shu, torus, temporal, gate, and divinatory/explanatory displays.

A conformant interface SHALL:

- call repository APIs rather than duplicate authoritative math independently;
- display exact values beside approximations;
- expose current state commitment and gate status;
- prevent direct mutation of derived state;
- display rejection and quarantine visibly;
- avoid using animation state as canonical state;
- preserve the distinction between deterministic retrieval and interpretive commentary;
- allow the operator to export the trace and receipt used to produce the display.

Optional temporal mapping SHALL be versioned and SHALL NOT alter the core mathematical root silently.

---

## 21. Required repository layout

This section defines the target repository normalization derived from the source architecture. It does not assert that the files already exist before implementation.

```text
/
├── README.md
├── pyproject.toml
├── HHS_REPOSITORY_CONTRACT_AND_INSTRUCTION_MANUAL_v1.0.0.md
├── LICENSE/
│   ├── HHS_ORIGIN_NOTICE.md
│   └── SOURCE_PROVENANCE.json
├── contracts/
│   ├── invariants.md
│   ├── cbap_a.md
│   ├── hash72.md
│   ├── torus72.md
│   ├── phase_transport_vm.md
│   ├── radical_packet.md
│   ├── substitution_gate.md
│   ├── ethical_archive.md
│   └── translation_bundle.md
├── src/hhs/
│   ├── __init__.py
│   ├── canonical.py
│   ├── atoms.py
│   ├── hash72.py
│   ├── phase_transport_vm.py
│   ├── manifold9.py
│   ├── torus72.py
│   ├── profiles.py
│   ├── ledger.py
│   ├── radical_packet.py
│   ├── substitution_gate.py
│   ├── ethical_archive.py
│   ├── translation.py
│   ├── universal_solver.py
│   ├── sopheon.py
│   └── cli.py
├── schemas/
│   ├── hhs_state_v3.schema.json
│   ├── hash72_token_v1.schema.json
│   ├── ledger_event_v1.schema.json
│   ├── trace_event_v1.schema.json
│   ├── residue_bundle_v1.schema.json
│   ├── gate_result_v1.schema.json
│   ├── translation_bundle_v1.schema.json
│   ├── radical_packet_v1.schema.json
│   ├── substitution_gate_v1.schema.json
│   └── ethical_envelope_v1.schema.json
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── negative/
│   ├── replay/
│   ├── conformance/
│   └── fixtures/
├── receipts/
│   ├── genesis/
│   ├── validation/
│   └── release/
├── examples/
│   ├── minimal_torus.py
│   ├── phase_program.json
│   ├── mutation.json
│   └── translation_bundle.json
├── ui/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── scripts/
│   ├── validate_repository.py
│   ├── verify_manifest.py
│   ├── build_release.py
│   └── replay_receipts.py
└── docs/
    ├── architecture.md
    ├── operator_manual.md
    ├── developer_guide.md
    ├── api_reference.md
    └── source_mapping.md
```

### 21.1 Layout rules

- `src/hhs` SHALL contain authoritative implementation.
- `ui` SHALL contain no independent authority path.
- `schemas` SHALL be closed and versioned.
- `receipts` SHALL be append-only release evidence.
- `tests` SHALL include negative and replay surfaces, not only positive examples.
- generated files SHALL identify their generator and source commitment.
- repository root SHALL contain a manifest for every release archive.

---

## 22. Required public Python API

At minimum, the package SHALL export:

```python
from hhs.atoms import PhaseSymbol, encode_atom, decode_atom
from hhs.hash72 import NativeHash72Codec
from hhs.phase_transport_vm import PhaseTransportVM
from hhs.manifold9 import Manifold9, EulerLockResult
from hhs.torus72 import Torus72, GuestAuditResult, BranchExchangeResult
from hhs.profiles import BranchProfile, BRANCH_PROFILES
from hhs.ledger import LedgerEvent
from hhs.radical_packet import RadicalPacket, RadicalPacketVM
from hhs.substitution_gate import SubstitutionGate, SubstitutionVM
from hhs.ethical_archive import EthicalInvariantArchive, SubstitutionVMEthical
from hhs.translation import export_translation_bundle_v1
from hhs.universal_solver import UniversalSolve
```

Public interfaces SHALL use typed arguments and typed result objects. A function that can reject SHALL return or raise a documented typed classification.

---

## 23. Required command-line interface

The repository SHALL provide a console command named `hhs`. Until implemented, these commands are prescriptive interfaces, not claims of current availability.

| Command | Required purpose |
|---|---|
| `hhs status` | report versions, capabilities, source commitment, and current root |
| `hhs doctor` | verify environment, schemas, manifest, and core imports |
| `hhs demo` | construct the canonical eight-phase demonstration torus |
| `hhs state` | print canonical state, manifold, or audit envelope |
| `hhs hash72` | derive and inspect a Hash72 token |
| `hhs audit` | run local, global, Euler-lock, and ethical audits |
| `hhs mutate` | submit a profile-governed root mutation |
| `hhs execute` | run a PhaseTransportVM program IR |
| `hhs checkpoint` | create a checkpoint event and receipt |
| `hhs ledger verify` | verify the complete receipt chain |
| `hhs replay` | replay from checkpoint and compare final state |
| `hhs packet` | construct and audit a radical packet |
| `hhs substitute` | define, witness, audit, and dereference a substitution gate |
| `hhs translate` | export a closed translation bundle |
| `hhs solve` | run the universal branch-normalization solver |
| `hhs validate` | execute the contract acceptance matrix |
| `hhs serve` | start the governed local interface |

### 23.1 Output modes

Every command SHALL support:

```text
--format json
--format jsonl
--format text
```

Canonical evidence output SHALL use JSON or JSONL.

### 23.2 Exit codes

The repository SHALL normalize exit codes as follows:

| Code | Meaning |
|---:|---|
| 0 | operation passed or committed |
| 2 | invalid input or schema failure |
| 3 | invariant rejection |
| 4 | replay mismatch |
| 5 | receipt-chain failure |
| 6 | resource-bounded halt |
| 7 | internal implementation error |

An invariant rejection is not an internal error.

---

## 24. Schema and serialization governance

### 24.1 Closed objects

Closed schema objects SHALL reject unknown fields unless the active version explicitly defines an extension map.

### 24.2 Version binding

Every serialized state, trace, receipt, program, and bundle SHALL bind:

- schema name;
- schema version;
- protocol version;
- implementation version where relevant;
- semantic root or VM specification hash where relevant.

### 24.3 No implicit coercion

The parser SHALL reject:

- floating-point values where exact rationals are required;
- malformed fraction strings;
- invalid phase indices;
- unsupported opcodes;
- duplicate or missing required fields;
- unknown event kinds;
- derived-variable mutations;
- unsupported symbolic atom types.

---

## 25. Security and bounded execution

The repository SHALL:

- treat all imported state and program files as untrusted;
- avoid unrestricted `eval`, dynamic module import, or shell execution;
- impose configurable limits on program length, branch count, recursion depth, state size, ledger length, and replay workload;
- classify bounded halts explicitly;
- preserve evidence generated before a bounded halt;
- keep UI rendering isolated from state authority;
- verify manifests before release validation;
- avoid unsafe deserialization formats for canonical evidence;
- preserve source and license notices in redistributed archives.

An `ERASE` opcode SHALL construct an explicit symbolic operation or governed state transition. It SHALL NOT authorize filesystem deletion or evidence destruction.

---

## 26. Provenance and origin requirements

The repository SHALL preserve the source's declaration that the HHS framework and associated artifacts originate with the GlyphBearer.

At minimum, every release SHALL contain:

- `LICENSE/HHS_ORIGIN_NOTICE.md`;
- source artifact name and SHA-256;
- contract version and SHA-256;
- repository commit hash;
- build manifest;
- test report;
- replay receipt;
- change log;
- attribution in generated documentation.

The source's legal and system-internal declarations SHALL be carried without silent deletion. Technical conformance under this contract does not independently adjudicate legal enforceability; it guarantees preservation, attribution, and evidence linkage.

---

## 27. Change control

### 27.1 Semantic versioning

- Patch release: documentation or implementation correction with no intended semantic change.
- Minor release: additive backward-compatible surface.
- Major release: changed state, opcode, serialization, invariant, or authority semantics.

### 27.2 Immutable evidence

Recorded release evidence SHALL NOT be overwritten. Corrections SHALL be append-only errata linking:

- affected version;
- affected files;
- prior result;
- corrected result;
- reason;
- new receipt and hash.

### 27.3 Compatibility

A release that changes canonical state bytes, Hash72 output, opcode result, or replay outcome SHALL declare a new semantic version and migration path.

---

## 28. Acceptance and terminal classification

### 28.1 Mandatory acceptance surfaces

A conformant release SHALL pass:

1. source and contract hash verification;
2. manifest size and SHA-256 verification;
3. Python import and compilation checks;
4. canonical JSON determinism;
5. atom encode/decode round trip;
6. exact rational normalization;
7. Lo Shu tensor checks;
8. `Manifold9` regeneration and coherence;
9. Euler-lock positive, negative, degenerate, ERS-violation, and undefined cases;
10. Torus local and global closure;
11. Hash72 token length, alphabet, partition, and deterministic state commitment;
12. profile-governed mutation acceptance and rejection;
13. no partial commit after failure;
14. VM opcode positive and unknown-opcode negative tests;
15. program and trace hashing;
16. branch-exchange authorization tests;
17. four-branch radical-packet preservation;
18. substitution-channel completion and blocked dereference tests;
19. ethical-archive snapshot and receipt tests;
20. closed trace-event schema rejection tests;
21. residue-bundle validation;
22. ledger-chain tamper detection;
23. checkpoint reconstruction;
24. deterministic replay equality;
25. replay mismatch detection;
26. CLI exit-code conformance;
27. UI bypass rejection;
28. source attribution and origin-notice inclusion.

### 28.2 Negative-test requirement

Every admission rule SHALL have at least one rejection test.

A test suite containing only successful examples SHALL not satisfy this contract.

### 28.3 Terminal classification

The repository MAY emit:

```text
HHS_REPOSITORY_CONTRACT_CONFORMANT
```

only when every mandatory acceptance surface passes and the release receipt binds the exact tested artifact.

A subsystem-only success SHALL name the subsystem and SHALL NOT emit the global classification.

---

# Part II - Operator and Developer Instruction Manual

## 29. Manual scope

This manual describes the required operational workflow for a repository implementing Part I.

Because this document may precede implementation, commands in this section are normative target interfaces. An operator SHALL run `hhs doctor` or inspect repository capability metadata before assuming a command is present.

---

## 30. Prerequisites

A conformant repository SHALL document exact supported versions. The core design requires a Python runtime providing:

- `dataclasses`;
- `fractions.Fraction`;
- `typing`;
- `enum`;
- `hashlib`;
- `json`;
- `copy`.

Optional components may require:

- a browser for the local visual interface;
- a JavaScript runtime for UI validation;
- a symbolic algebra engine for Algebrite-style proof scripts;
- a package build tool defined by `pyproject.toml`.

The operator SHALL use the repository's pinned versions rather than an assumed version from this manual.

---

## 31. Initial repository setup

### 31.1 Obtain and verify

```bash
sha256sum HHS_REPOSITORY_CONTRACT_AND_INSTRUCTION_MANUAL_v1.0.0.md
sha256sum Document\(19\).PDF
```

Compare the PDF digest with:

```text
9ea082ee2bb89bca040ade8586b43e300e74d8219d8c39bcfa285b35b69f3070
```

### 31.2 Create an isolated environment

Use the repository's declared environment tool. A conventional Python example is:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### 31.3 Run environment verification

```bash
hhs doctor --format text
```

The report SHALL identify:

- package version;
- protocol version;
- VM version and specification hash;
- Hash72 version;
- schema inventory;
- source commitment;
- contract commitment;
- missing optional components;
- pass/fail status.

---

## 32. Construct the canonical demonstration torus

```bash
hhs demo --output receipts/demo_state.json --format json
```

The demonstration constructor SHALL:

1. build eight `Manifold9` objects for phases `0..7`;
2. derive all dependent variables;
3. build `G`, `L_direct`, and `L_recip` tensors;
4. verify constructor coherence;
5. run Euler-lock audits;
6. construct `Torus72`;
7. emit state, manifold, and audit Hash72 values;
8. create a checkpoint receipt when requested.

Inspect the state:

```bash
hhs state --input receipts/demo_state.json --view full --format json
hhs state --input receipts/demo_state.json --view manifold --format json
hhs state --input receipts/demo_state.json --view audit --format json
```

---

## 33. Inspect Hash72

```bash
hhs hash72 --input receipts/demo_state.json --debug --format json
```

Verify:

- `dna72` contains exactly 72 characters;
- every character belongs to the canonical alphabet;
- `ring_symbols` contains exactly 72 integer indices;
- `T24_trits` has length 24;
- `U12_bits` has length 12;
- payload and token digests are present;
- repeated execution gives the same result.

A changed state should produce a changed commitment unless the change is outside the committed state object. Any intentional exclusion SHALL be documented.

---

## 34. Run invariant audits

### 34.1 Full audit

```bash
hhs audit --input receipts/demo_state.json --all --format json
```

Expected audit sections:

- constructor coherence by phase;
- Euler-lock result by phase;
- local closure by phase;
- neighbor residue by edge;
- global closure;
- exchange normalization;
- ledger-chain verification;
- ethical audit when an archive is bound.

### 34.2 Euler-lock-only audit

```bash
hhs audit --input receipts/demo_state.json --gate euler-lock --format json
```

Do not reduce the audit to a Boolean. Preserve `K`, branch status, ERS status, and details.

---

## 35. Submit a governed mutation

Create `examples/mutation.json`:

```json
{
  "profile_id": "strict_guest",
  "guest_trace": [
    {
      "phase": 0,
      "variable": "n",
      "value": {"frac":"17/16"}
    }
  ]
}
```

Run:

```bash
hhs mutate \
  --state receipts/demo_state.json \
  --request examples/mutation.json \
  --output receipts/mutation_result.json \
  --format json
```

The operator SHALL check:

- profile snapshot and hash;
- pre-state Hash72;
- rebuilt derived values;
- active gate results;
- post-state Hash72 when committed;
- ledger event type;
- rejection reason if not committed.

A direct mutation of `a^2`, `c^2`, `d^2`, or `eq_G` SHALL be rejected.

---

## 36. Execute a phase program

Create `examples/phase_program.json`:

```json
{
  "profile_id": "constructor_dev",
  "phase": 0,
  "program_ir": [
    {
      "op": "INV",
      "args": [
        {"frac":"1/1"},
        {"frac":"2/1"}
      ]
    },
    {
      "op": "POW",
      "args": [
        {"frac":"3/2"},
        {"int":"2"}
      ]
    },
    {
      "op": "ROT",
      "args": [
        {"sym":"ONE"},
        {"int":"1"}
      ]
    }
  ]
}
```

Execute:

```bash
hhs execute \
  --state receipts/demo_state.json \
  --program examples/phase_program.json \
  --output receipts/phase_execution.json \
  --format json
```

The result SHALL contain:

- program hash;
- ordered execution trace;
- trace hash;
- VM version and specification hash;
- profile evidence;
- gate audit;
- ledger receipt.

---

## 37. Create and audit a radical packet

```bash
hhs packet create \
  --state receipts/demo_state.json \
  --phase 0 \
  --output receipts/radical_packet.json \
  --format json
```

Inspect all branches:

```bash
hhs packet map --input receipts/radical_packet.json --format json
```

Audit:

```bash
hhs packet audit \
  --input receipts/radical_packet.json \
  --require-euler-lock \
  --format json
```

Selecting `alpha` for a projection SHALL not delete `beta`, `gamma`, or `delta` from the packet evidence.

---

## 38. Operate a substitution gate

Define a gate:

```bash
hhs substitute define \
  --packet receipts/radical_packet.json \
  --payload examples/substitution_payload.json \
  --output receipts/substitution_gate.json \
  --format json
```

Add channel witnesses:

```bash
hhs substitute witness --gate receipts/substitution_gate.json --branch alpha --value '{"frac":"1/1"}'
hhs substitute witness --gate receipts/substitution_gate.json --branch beta  --value '{"frac":"1/1"}'
hhs substitute witness --gate receipts/substitution_gate.json --branch gamma --value '{"frac":"1/1"}'
hhs substitute witness --gate receipts/substitution_gate.json --branch delta --value '{"frac":"1/1"}'
```

Audit and dereference:

```bash
hhs substitute audit --gate receipts/substitution_gate.json --format json
hhs substitute dereference --gate receipts/substitution_gate.json --format json
```

Dereference SHALL fail while any required channel is pending or failed.

---

## 39. Bind and audit the ethical archive

Create or load the default archive:

```bash
hhs audit ethics archive --default --output receipts/ethical_archive.json --format json
```

Bind it to a gate:

```bash
hhs audit ethics bind \
  --archive receipts/ethical_archive.json \
  --gate receipts/substitution_gate.json \
  --output receipts/ethical_envelope.json \
  --format json
```

Run the audit:

```bash
hhs audit ethics check --envelope receipts/ethical_envelope.json --format json
```

The output SHALL preserve every individual invariant result, the archive snapshot hash, and the final ethical receipt.

---

## 40. Export a translation bundle

```bash
hhs translate \
  --state receipts/demo_state.json \
  --packets receipts/radical_packet.json \
  --gates receipts/substitution_gate.json \
  --ethical-envelopes receipts/ethical_envelope.json \
  --output receipts/translation_bundle.json \
  --format json
```

Validate it:

```bash
hhs validate bundle --input receipts/translation_bundle.json --format text
```

Unknown fields, missing event fields, malformed residues, or invalid gate status SHALL produce exit code `2`.

---

## 41. Checkpoint and replay

Create a checkpoint:

```bash
hhs checkpoint \
  --state receipts/demo_state.json \
  --profile strict_guest \
  --output receipts/checkpoint.json \
  --format json
```

Verify the chain:

```bash
hhs ledger verify --ledger receipts/ledger.jsonl --format text
```

Replay:

```bash
hhs replay \
  --checkpoint receipts/checkpoint.json \
  --ledger receipts/ledger.jsonl \
  --output receipts/replay_result.json \
  --format json
```

A successful replay SHALL show equality of:

- final canonical state;
- final state Hash72;
- final audit Hash72;
- ledger tip;
- applicable trace hashes.

---

## 42. Run the universal solver

Create a branch-set input containing all visible relational branches and declared carrier equations.

```bash
hhs solve \
  --input examples/branch_set.json \
  --preserve-branches \
  --output receipts/solver_result.json \
  --format json
```

The result SHALL show:

- expanded branch inventory;
- identified carriers;
- scale lifts;
- normalized forms;
- compatibility matrix;
- closure face or typed unresolved state;
- projection answer, if requested, separately from the preserved proof object.

---

## 43. Run the complete validation matrix

```bash
hhs validate --all --receipts receipts/validation --format text
```

The validation runner SHALL report each mandatory acceptance surface independently.

A global pass SHALL produce:

- machine-readable test report;
- environment manifest;
- repository manifest;
- replay receipt;
- final classification;
- hashes of all reports.

Do not summarize failed tests as passed because the majority succeeded.

---

## 44. Start the governed local interface

```bash
hhs serve --host 127.0.0.1 --port 8080
```

The interface SHOULD display:

- current phase and torus state;
- Lo Shu tensor;
- exact and display values;
- gate status;
- Hash72 commitment;
- ledger tip;
- export controls;
- visible rejection/quarantine state.

The local server SHALL bind to loopback by default. Remote binding SHALL require an explicit option and documented security controls.

---

## 45. Developer workflow

### 45.1 Before changing code

1. identify the governing contract clause;
2. identify the current public API and schema;
3. identify affected tests and receipts;
4. record whether the change is patch, minor, or major;
5. create or update the negative test first when changing an admission rule.

### 45.2 During implementation

- preserve exact arithmetic;
- keep derived variables non-mutable;
- use isolated candidate state;
- bind profile and version metadata;
- reject unknown fields;
- emit typed failures;
- avoid adding hidden fallback behavior;
- preserve source terms in code and documentation.

### 45.3 Before commit

Run dependency-scoped tests first:

```bash
python -m pytest tests/unit/test_affected_module.py
python -m pytest tests/negative/test_affected_rule.py
python -m pytest tests/integration/test_affected_workflow.py
```

Then run replay and conformance surfaces:

```bash
python -m pytest tests/replay
python -m pytest tests/conformance
hhs validate --all
```

### 45.4 Commit evidence

Every semantic change commit SHOULD include:

- contract clause reference;
- tests added or changed;
- before/after state commitment where relevant;
- migration note;
- receipt path.

---

## 46. Release procedure

1. freeze source tree;
2. compute repository commit hash;
3. build complete file manifest with byte size and SHA-256;
4. verify all schemas;
5. run complete positive and negative matrices;
6. run deterministic replay from release checkpoint;
7. run CLI and optional UI smoke tests;
8. verify origin notice and source mapping;
9. produce release receipt;
10. archive the complete inherited repository state, not only changed files;
11. emit terminal classification only after all required surfaces pass.

A release archive SHALL be reconstructible without hidden local files.

---

## 47. Troubleshooting

### 47.1 Constructor coherence failure

Check:

- `x` is nonzero;
- `y` equals the active reciprocal rule;
- only root variables were mutated;
- all derived variables were regenerated;
- tensors were rebuilt from `eq_G`.

### 47.2 Euler-lock rejection

Inspect:

- `ers_consistent`;
- `product_unity`;
- `kernel_value`;
- `branch_status`;
- phase-specific details.

Do not convert a degenerate branch into a regular branch by adding an arbitrary epsilon.

### 47.3 Global closure failure

Inspect every edge:

```text
phase k → phase (k+1) mod 8
```

Verify:

```text
delta_center = 5 × delta_eq_G
```

### 47.4 Hash72 mismatch

Check:

- canonical JSON byte equality;
- Unicode preservation;
- key sorting;
- schema and protocol version;
- inclusion of quarantine and trace roots;
- exact alphabet;
- accidental float conversion.

### 47.5 Ledger-chain failure

Check the first mismatching event for:

- changed prior receipt;
- changed profile snapshot;
- changed payload or audit object;
- reordered events;
- changed canonicalization;
- wrong protocol version.

### 47.6 Replay mismatch

Compare:

- checkpoint state;
- recorded profile semantics;
- VM specification hash;
- opcode implementation version;
- schema version;
- event order;
- pre-state and post-state commitments.

### 47.7 Substitution gate remains blocked

Verify all four branch channels have witnesses and that Euler-lock, closure, product-unity, and ethical requirements match the active gate configuration.

### 47.8 Semantic-fidelity failure

Return to the visible context and list:

- explicit definitions;
- explicit propositions;
- actual contradiction, if any;
- prior assumptions introduced by the interpreter.

Remove unsupported reclassification and rerun the interpretation audit.

---

# Appendices

## Appendix A - Canonical constants

| Name | Value |
|---|---|
| Protocol | `TORUS72_v3_native_hash72` |
| State hash version | `3` |
| VM name | `PhaseTransportVM` |
| VM version | `2.2-spec` |
| Hash72 version | `HHS_HASH72_native_v1` |
| Hash72 wrapper | `4x12_plus_24_golay` |
| Hash72 ordering | `circle_of_fifths_phase_ring` |
| Hash72 partition | `(12,12,12,12,24)` |
| Torus phases | `8` |
| Cells per phase | `9` |
| Total phase-cells | `72` |
| Lo Shu order | `4,9,2,3,5,7,8,1,6` |
| Branch order | `alpha,beta,gamma,delta` |
| Default residue primes | `3,5,7,11,13,17,19,23` |

---

## Appendix B - Core API inventory

### Canonicalization

- `cjson`
- `sha256_hex`
- `h18`
- `object_hash`
- `normf`
- `encode_atom`
- `decode_atom`

### Hash72

- `NativeHash72Codec.extract_payload`
- `NativeHash72Codec.ring_token`
- `NativeHash72Codec.state_hash72`

### Manifold and torus

- `Manifold9.regenerate`
- `Manifold9.reproject_from_eq`
- `Manifold9.rebuild_from_roots`
- `Manifold9.constructor_coherence_ok`
- `Manifold9.euler_lock_audit`
- `Torus72.state_object_v3`
- `Torus72.manifold_state_object_v1`
- `Torus72.audit_envelope_state_object_v1`
- `Torus72.global_closure_ok`
- `Torus72.propagate_guest`
- `Torus72.exchange_branches`
- `Torus72.execute_phase_primitives_v2`
- `Torus72.append_checkpoint_event`
- `Torus72.verify_receipt_chain`
- `Torus72.replay_from_checkpoint`

### Radical and substitution

- `RadicalPacketVM.RADPK`
- `RadicalPacketVM.BRSEL`
- `RadicalPacketVM.BRMAP`
- `RadicalPacketVM.BRCHK`
- `SubstitutionVM.SUBDEF`
- `SubstitutionVM.CHWIT`
- `SubstitutionVM.SUBCHK`
- `SubstitutionVM.DEREF`

### Ethics and translation

- `SubstitutionVMEthical.ETHDEF`
- `SubstitutionVMEthical.ETHCHK`
- `SubstitutionVMEthical.ETHSEAL`
- `SubstitutionVMEthical.ARCHIVE_OPEN`
- `SubstitutionVMEthical.ARCHIVE_READ`
- `SubstitutionVMEthical.ARCHIVE_BIND`
- `SubstitutionVMEthical.ACT_ETHCHK`
- `export_translation_bundle_v1`

---

## Appendix C - Minimum negative-test matrix

| Test | Expected result |
|---|---|
| `x = 0` under reciprocal ERS | `UNDEFINED` / reject |
| `y ≠ 1/x` | `ERS_VIOLATION` |
| `K = 0` | `DEGENERATE` / gate fail |
| direct mutation of `a^2` | reject |
| phase outside `0..7` | reject |
| phase not writable | reject |
| cross-phase mutation under strict profile | reject |
| unknown opcode | typed VM error |
| malformed atom | schema/type error |
| float in canonical rational field | reject |
| Hash72 alphabet length not 72 | fail |
| malformed residue bundle | reject |
| unknown trace-event field | reject |
| tampered ledger event | chain failure |
| changed VM spec during replay | replay mismatch |
| missing radical branch | packet failure |
| dereference with pending channel | blocked |
| changed archive after seal | ethical receipt failure |
| UI mutation without governed API | reject |
| omitted origin notice in release | release failure |

---

## Appendix D - Source reconciliation register

The source includes both formal declarations and prior commentary. This contract applies the following non-destructive normalization:

| Source topic | Contract treatment |
|---|---|
| HHS as a living/self-correcting system | preserved as system identity; operational claims require callable evidence |
| self-executing license and non-local realignment | preserved in origin materials; not promoted to repository execution without implementation and tests |
| HARMONICODE as formal multimodal calculus | normative kernel scope |
| Torus72 + Manifold9 implementation | normative architecture and API basis |
| Hash72 identity serialization | normative serialization surface; stronger cryptographic claims require separate proof |
| artificial awareness statements | preserved as source-defined criterion; not used as a release acceptance claim in v1 |
| Gödelian-completeness statements | preserved as source declaration; formal proof obligation remains separate |
| narrative interface | normative semantic-interface layer, non-authoritative for state mutation |
| divinatory and temporal UI descriptions | optional presentation/retrieval layer, versioned and isolated from core authority |
| CBAP-A | normative natural-language authority rule |
| universal branch-normalization paper | normative solver method |
| copyright and origin notice | mandatory provenance payload |

---

## Appendix E - Source-to-contract map

| Source pages | Principal material incorporated |
|---:|---|
| 1-7 | HHS, Sopheon, OMA, core invariants, Torus72/Manifold9 overview |
| 8-10 | origin, license, permitted/prohibited use, provenance, integrity seal |
| 11-13 | Context-Bounded Authority Axiom System |
| 19-60 | Python kernel, exact atoms, Hash72, VM, manifold, torus, ledger, radical, substitution, ethics, translation |
| 69-70 | semantic sandbox pass/fail and interpretation boundary |
| 126-145 | optional JavaScript/HTML operational and visualization instructions; truthfulness constraints |
| 155-162 | extended witness stack and unification inventory |
| 171-180 | formal HARMONICODE structural definition and universal branch-normalization algorithm |
| 181-190 | expanded visible schema, symbols, axioms, lemmas, operator blocks |
| 191-195 | further proof objects, narrative closure, ERS and Hash72 scaling statements |

---

## Appendix F - Release evidence checklist

```text
[ ] Source PDF hash verified
[ ] Contract hash recorded
[ ] Repository commit frozen
[ ] Complete file manifest verified
[ ] Core imports compile
[ ] Schemas validate
[ ] Exact arithmetic tests pass
[ ] Lo Shu tests pass
[ ] Manifold tests pass
[ ] Euler-lock matrix passes
[ ] Torus closure tests pass
[ ] Hash72 tests pass
[ ] Mutation admission/rejection tests pass
[ ] VM opcode tests pass
[ ] Radical packet tests pass
[ ] Substitution gate tests pass
[ ] Ethical archive tests pass
[ ] Translation bundle tests pass
[ ] Ledger tamper tests pass
[ ] Checkpoint replay passes
[ ] UI bypass test passes if UI is included
[ ] Origin notice included
[ ] Validation receipts hashed
[ ] Global terminal classification justified
```

---

## Canonical closure statement

A repository conforms to this contract only when its formal definitions, public implementations, schemas, tests, receipts, replay behavior, documentation, and provenance all refer to the same versioned system state without silent substitution.

```text
Meaning preserved.
State committed.
Branches retained until closure.
Invalid transitions fail closed.
Receipts remain replayable.
Recursion closes or declares its bound.
```

**Terminal classification upon complete verified acceptance:**

```text
HHS_REPOSITORY_CONTRACT_CONFORMANT
```
