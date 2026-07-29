# HHS PASS 172 — DEPENDENCY AUTHORITY AND COMPATIBLE ENVIRONMENT NORMALIZATION CONTRACT

## Deterministic Dependency Surfaces, Profile-Scoped Substrate Adapters, Canonical Runtime Authority Preservation, and Receipt-Closed Compatibility Verification

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P172-DA-CEN` |
| Pass number | `172` |
| Canonical pass name | `DEPENDENCY_AUTHORITY_AND_COMPATIBLE_ENVIRONMENT_NORMALIZATION_CONTRACT` |
| Short name | `P172 Dependency Normalization` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | Current authoritative `main`, including complete Pass 170 and Pass 171 contracts and inherited accepted history |
| Immediate inheritance parent | Complete authoritative Pass 171 inherited pass-history nucleus |
| Canonical execution authority | Exactly one VM81 runtime authority |
| Canonical mutation authority | Exactly one admitted VM81 commit path |
| Public operation authority | Pass 170 governed public API registry and gateway rules |
| Numeric/kernel authority | Inherited exact arithmetic and invariant requirements; no canonical float authority |
| Execution evidence | Hash72 |
| Source/state identity | Hash216 |
| Validation model | Dependency-scoped, profile-bounded, repair-forward |
| Initial classification | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |

# 2. Normative language

The terms **SHALL**, **SHALL NOT**, **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

Pass 172 is an implementation-and-normalization pass. Inventory-only reporting SHALL NOT satisfy this contract.

Pass 172 SHALL remain nonterminal until dependency acquisition, compatibility profile selection, and runtime preflight are deterministic, governed, and replayable through inherited authorities.

# 3. Governing invariants

```text
DEPENDENCY_USED
⇒ DECLARED_IN_CANONICAL_SURFACE
∧ PROFILE_SCOPED
∧ VERSION_POLICY_DEFINED
∧ INTEGRITY_CHECKED
∧ AUTHORITY_PATH_PRESERVED
∧ HASH72_EVIDENCE_EMITTED
```

```text
ENVIRONMENT_COMPATIBLE
⇒ PRECHECK_PASSED
∧ REQUIRED_SUBSTRATE_PRESENT
∧ NO_PRIVATE_BYPASS
∧ NO_PARALLEL_COMMIT_AUTHORITY
```

Equivalent rejection form:

```text
UNDECLARED_DEPENDENCY ∨ UNREGISTERED_ENVIRONMENT_PATH ⇒ REJECT
```

# 4. Scope and required dependency authorities

Pass 172 SHALL normalize dependency authority across all active surfaces:

1. Python runtime and service surfaces.
2. LiteRT-LM provider bootstrap surfaces.
3. Native C/ABI build surfaces.
4. Node/UI surfaces.
5. Deployment/container surfaces.
6. Workflow/test execution surfaces used for release admission.

For each surface, the repository SHALL define:

- canonical source file(s);
- compatible version policy;
- profile applicability;
- preflight checks;
- failure mode and closure behavior;
- receipt/evidence projection.

# 5. Compatibility profiles

Pass 172 SHALL define and enforce at least these compatible profiles:

1. `cpu-local`
2. `gpu-local`
3. `external-provider`

Each profile SHALL include:

- required software toolchain;
- required OS/runtime substrate conditions;
- disallowed assumptions;
- explicit preflight gates;
- deterministic fallback or reject behavior.

Profiles SHALL NOT alter canonical VM81 mutation authority or create alternate commit paths.

# 6. Forbidden behaviors

No Pass 172 component may:

- fetch or execute undeclared runtime dependencies as hidden side effects;
- treat CI-only tooling as implicit runtime dependency without explicit classification;
- bypass the Pass 170 public gateway rules for externally meaningful operations;
- introduce separate ledgers, receipts, or authority roots outside Hash72/Hash216 lineage;
- classify approximate or float-only results as canonical kernel state;
- weaken inherited invariants (`Δe=0`, `Ψ=0`, `Θ15=true`, `Ω=true`) for environment convenience.

# 7. Required result

Pass 172 SHALL produce a governed dependency-and-compatibility contract layer that:

1. maps all requirement files and package manifests to canonical profiles;
2. defines deterministic installation order by profile;
3. defines explicit system-package adapters where substrate setup is required;
4. marks optional vs mandatory dependencies by profile;
5. records compatibility preflight outcomes in receipt-linked evidence;
6. rejects unscoped dependencies or unverified substrate assumptions;
7. preserves replayability of dependency resolution and preflight decisions.

# 8. Acceptance requirements

Pass 172 acceptance requires executable evidence that:

1. profile selection is explicit and validated;
2. undeclared dependency use is rejected;
3. declared dependency surfaces resolve deterministically for supported profiles;
4. substrate preflight produces bounded, machine-readable closure;
5. no alternate runtime/mutation authority is introduced;
6. inherited Pass 170 and 171 constraints remain satisfied;
7. all outcomes are receipt-linked and replay-verifiable.

# 9. Classification policy

If Pass 171 parent closure is unresolved, the highest permitted Pass 172 classification is:

```text
HHS_PASS_172_IMPLEMENTATION_VERIFIED_PENDING_PASS_171_PARENT_RESOLUTION
```

Terminal Pass 172 classification requires parent closure plus complete acceptance evidence:

```text
HHS_PASS_172_DEPENDENCY_AND_ENVIRONMENT_NORMALIZATION_LIVE_VERIFIED
```

