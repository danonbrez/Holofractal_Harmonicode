# HHS PASS 173 — ONE-COMMAND INSTALLATION AND COMPATIBLE ENVIRONMENT BOOTSTRAP CONTRACT

## Canonical Bootstrap Entry, Profile-Governed Substrate Verification, Deterministic Dependency Resolution, Runtime Authority Preservation, and Receipt-Closed Startup

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P173-OCI-CEB` |
| Pass number | `173` |
| Canonical pass name | `ONE_COMMAND_INSTALLATION_AND_COMPATIBLE_ENVIRONMENT_BOOTSTRAP_CONTRACT` |
| Short name | `P173 One-Command Install` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | Current authoritative `main`, including complete Pass 170, Pass 171, and Pass 172 contract requirements |
| Immediate inheritance parent | Complete authoritative Pass 172 inherited pass-history nucleus |
| Canonical execution authority | Exactly one VM81 runtime authority |
| Canonical mutation authority | Exactly one admitted VM81 commit path |
| Public operation authority | Inherited Pass 170 governed public API model |
| Dependency authority | Inherited Pass 172 normalized dependency/profile authority |
| Execution evidence | Hash72 |
| Source/state identity | Hash216 |
| Validation model | Dependency-scoped, staged bootstrap gate, repair-forward |
| Initial classification | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |

# 2. Normative language

The terms **SHALL**, **SHALL NOT**, **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

Pass 173 defines the authoritative one-command installation and startup contract for compatible environments.

Pass 173 SHALL remain nonterminal until a single canonical bootstrap command can execute deterministic install, verification, and startup closure for each declared compatible profile.

# 3. Governing invariant

```text
ONE_COMMAND_BOOTSTRAP_REQUESTED
⇒ CANONICAL_ENTRY_SELECTED
∧ PROFILE_VALIDATED
∧ PREFLIGHT_PASSED
∧ DEPENDENCY_PLAN_RESOLVED
∧ AUTHORITY_PATH_PRESERVED
∧ STARTUP_VERIFIED
∧ HASH72_BOOTSTRAP_RECEIPT_EMITTED
```

Equivalent rejection form:

```text
NO_CANONICAL_ENTRY ∨ PROFILE_UNSCOPED ∨ AUTHORITY_BYPASS ⇒ REJECT
```

# 4. Canonical one-command contract

Pass 173 SHALL define one canonical user-facing bootstrap entry that performs:

1. profile selection and validation;
2. environment/toolchain preflight;
3. dependency installation or verification per profile;
4. substrate checks (including accelerator substrate where required);
5. native/runtime verification gates;
6. startup handoff to canonical service launcher;
7. machine-readable closure and receipt projection.

Multiple helper scripts MAY exist, but one entry SHALL be the normative public bootstrap authority.

# 5. Compatible profile obligations

Pass 173 SHALL inherit and enforce Pass 172 profile contract for:

1. `cpu-local`
2. `gpu-local`
3. `external-provider`

For each profile, the one-command path SHALL define:

- mandatory prerequisites;
- optional prerequisites;
- strict reject conditions;
- degraded-mode policy (if allowed);
- terminal success criteria.

# 6. Authority preservation requirements

One-command bootstrap SHALL NOT:

- instantiate alternate canonical runtimes;
- create alternate commit/receipt ledgers;
- bypass public API governance for externally meaningful operations;
- authorize canonical mutation from installer-only code paths;
- weaken inherited kernel or algebraic authority constraints.

Installer/orchestrator logic SHALL be a thin adapter layer over existing canonical runtime, gateway, and provider authorities.

# 7. Determinism and replay

Pass 173 SHALL make bootstrap outcomes replayable by recording:

- selected profile;
- dependency inputs and resolved versions/policies;
- preflight results;
- verification gate outcomes;
- startup state and endpoint readiness;
- failure closure reason where applicable.

These records SHALL be receipt-linked and deterministic under equivalent inputs.

# 8. Security and closure requirements

The one-command contract SHALL:

1. fail closed on incompatible substrate or unmet mandatory dependency;
2. prevent silent partial-success classification;
3. avoid exposing unauthenticated upstream provider surfaces as canonical public gateway;
4. preserve capability boundaries inherited from prior passes;
5. prevent secrets from being embedded in static repository artifacts.

# 9. Acceptance requirements

Pass 173 acceptance requires executable evidence that:

1. one canonical bootstrap entry is defined and discoverable;
2. each compatible profile can be selected and validated;
3. successful profile runs complete install + verification + startup closure;
4. failed profile runs produce explicit reject closure;
5. inherited Pass 170 public API authority rules hold;
6. inherited Pass 171 singleton runtime/no-parallel-authority rules hold;
7. inherited Pass 172 dependency/profile normalization rules hold;
8. bootstrap evidence is receipt-linked and replay-verifiable.

# 10. Classification policy

If Pass 172 parent closure is unresolved, the highest permitted Pass 173 classification is:

```text
HHS_PASS_173_IMPLEMENTATION_VERIFIED_PENDING_PASS_172_PARENT_RESOLUTION
```

Terminal Pass 173 classification requires complete parent closure and acceptance evidence:

```text
HHS_PASS_173_ONE_COMMAND_INSTALLATION_LIVE_VERIFIED
```

