# Pass 172–173 compatible-constraint union binding

## 1. Status and scope

```yaml
binding_id: HHS-P172-P173-COMPATIBLE-CONSTRAINT-UNION-V1
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: 92dddbee21bae7e00b79b8f6f974501e039adc11
active_branch: agent/pass172-173-consolidation-implementation
intended_merge_target: main
status: BOUND_FOR_IMPLEMENTATION
contract_modification_authorized: false
constraint_deletion_authorized: false
constraint_weakening_authorized: false
```

This binding governs the consolidation and implementation of all repository-visible and supplied Pass 172 and Pass 173 variants.

It does **not** rewrite, replace, renumber, supersede, or delete either contract. The contract texts remain preserved as historical and normative source artifacts.

The implementation obligation is the compatible union of their requirements.

## 2. Source identities currently resolved

| Pass | Canonical path on authoritative base | Git blob SHA |
|---|---|---|
| 172 | `HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md` | `e50d3fe1dc095d803334c9636b6cfc43ae4deea5` |
| 173 | `HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md` | `293968b759deb6f86804465c1086d0382546b1a2` |

Additional variants discovered in repository history, branches, pull-request heads, user-supplied text, or future recovery artifacts SHALL be added to the provenance matrix without editing the source contracts.

## 3. Governing union rule

```text
ALL COMPATIBLE CONSTRAINTS ARE CUMULATIVE IMPLEMENTATION REQUIREMENTS.
```

For every requirement clause `r` discovered in any Pass 172 or Pass 173 variant:

```text
compatible(r, inherited_authority) = true
⇒ retain(r)
∧ map_to_implementation(r)
∧ map_to_test(r)
∧ map_to_evidence(r)
∧ require_terminal_closure(r)
```

No requirement may be omitted merely because another variant does not repeat it.

## 4. Constraint classification rules

Every discovered clause SHALL be classified by one of the following rules.

### 4.1 Identical clauses

Identical clauses are implemented once but retain every provenance reference.

```text
IDENTICAL(A,B)
⇒ one implementation obligation
∧ two provenance bindings
```

### 4.2 Additive clauses

Non-conflicting clauses are both mandatory.

```text
ADDITIVE(A,B)
⇒ A ∧ B
```

### 4.3 Stricter and weaker clauses

Where one clause is strictly stronger while remaining compatible, the stronger clause governs implementation and the weaker clause remains an inherited minimum.

```text
A ⇒ B
⇒ implement(A)
∧ preserve(B as minimum)
```

### 4.4 Profile-scoped clauses

Different profile requirements are not conflicts. They are implemented under their declared profiles and tested independently.

### 4.5 Platform-scoped clauses

Linux, macOS, Windows, Android, Termux, BSD, container, cloud, CPU, GPU, and external-provider requirements coexist at their actual declared boundaries.

### 4.6 Implementation and verification clauses

Pass 172 implementation requirements and Pass 173 independent-verification requirements are complementary.

```text
PASS_172_IMPLEMENTATION
∧ PASS_173_INDEPENDENT_VERIFICATION
```

Pass 173 SHALL not become a second installer, and Pass 172 self-reporting SHALL not replace Pass 173 reconstruction.

### 4.7 Apparent conflicts

A clause pair is a true conflict only if both cannot be satisfied under any explicit profile, platform, phase, authority, or state-machine partition.

True conflicts SHALL:

1. preserve both source clauses;
2. receive a machine-readable conflict identity;
3. record the exact contradiction;
4. block terminal closure;
5. require an explicit user-authorized resolution;
6. never be resolved through silent deletion or weakening.

## 5. Mandatory integrated authority constraints

The unified implementation SHALL preserve all of the following simultaneously:

```text
ONE PASS 172 INSTALLATION IMPLEMENTATION AUTHORITY
ONE PASS 173 VERIFICATION AND REPAIR AUTHORITY
ONE VM81 RUNTIME AUTHORITY
ONE ADMITTED VM81 COMMIT PATH
ONE HASH72 RECEIPT LINEAGE
ONE HASH216 INSTALLATION-IDENTITY MODEL
ONE CANONICAL PUBLIC API GATEWAY
```

Applications, installers, verification tools, deployment tools, and management surfaces SHALL be registered IDE public-API workflow compilations.

They SHALL NOT become parallel computation authorities outside the Runtime.

Installer host provisioning remains distinct from canonical Runtime computation:

```text
INSTALLER AUTHORITY != RUNTIME AUTHORITY
VERIFIER AUTHORITY != INSTALLER AUTHORITY
IDE WORKFLOW != PARALLEL RUNTIME
```

## 6. Mandatory Pass 172 implementation union

The implementation backlog SHALL include every compatible requirement concerning:

- capability-only environment probing before mutation;
- deterministic profile selection;
- source acquisition and supply-chain verification;
- dependency graph separation and platform locks;
- isolated Python environments;
- portable ISO C11 native builds;
- ABI and symbol verification;
- Node/frontend isolation;
- LiteRT-LM local GPU, local CPU, external, disabled, degraded, and incompatible states;
- model-asset governance;
- Linux, macOS, Windows, Android/Termux, BSD/POSIX, container, and restricted-cloud adapters;
- offline bundles with no network fallback;
- one-command POSIX, PowerShell, repository-local, Python, and offline entrypoints;
- transactional staging, activation, update, rollback, repair, and uninstall;
- user-data preservation;
- privilege-plan declaration and authorization;
- port and process safety;
- deterministic configuration generation;
- Hash216 installation identity;
- Hash72 installation receipts;
- public read-only installation status surfaces;
- IDE-registered local management proposals with authorization, expiry, and replay protection;
- bounded retries, timeouts, logs, recovery journals, and idempotence.

## 7. Mandatory Pass 173 verification union

The verification backlog SHALL include every compatible requirement concerning:

- static requirement and dependency traceability;
- clean-environment executed installation matrices;
- independent artifact and receipt reconstruction;
- fault injection and deterministic repair;
- redundant evidence for every load-bearing claim;
- platform, architecture, profile, provider, model, offline, container, Android, path, update, rollback, repair, and uninstall matrices;
- historical-evidence preservation and current-state supersession;
- native project inventory from the live tree;
- Python and Node dependency closure;
- receipt-count reconciliation from executed events;
- independent Hash72 chain verification;
- independent Hash216 installation-identity reconstruction;
- logical and full clean-environment replay;
- cross-platform semantic and ABI equivalence;
- security fault injection;
- repair-forward dependency-scoped revalidation;
- one bounded final replay;
- honest nonterminal classifications for unavailable real runners or hardware.

## 8. Stateless-resumable delivery constraint

Every implementation and verification step is additionally bound by:

```text
EVERY AGENTIC TASK MUST BE RESTARTABLE
FROM REPOSITORY-VISIBLE STATE ALONE.
```

Before a long-running or failure-prone step, the repository SHALL record:

- repository and authoritative base commit;
- active branch and merge target;
- changed files;
- commands already executed;
- validation results and remaining checks;
- environment and deployment state;
- exact next action;
- blocker details;
- timeouts and fallback behavior.

Every external command SHALL terminate as `SUCCESS`, `FAILURE`, or `BLOCKED` and SHALL have captured output, a timeout, and an idempotent resumption boundary.

## 9. Implementation merge policy

“Merge” means integration into shared authoritative implementation surfaces, not concatenation of contract prose.

The implementation SHALL prefer:

1. one canonical schema with versioned extensions;
2. one implementation module per authoritative responsibility;
3. shared primitives rather than duplicate semantics;
4. profile/platform adapters rather than forks of core authority;
5. one test identity per requirement with multiple evidence lanes;
6. historical source preservation plus additive implementation;
7. no parallel installer, verifier, Runtime, API, receipt, or state authority.

## 10. Required repository artifacts

The consolidation implementation SHALL produce and maintain:

```text
evidence/pass172_173/variant_inventory.json
evidence/pass172_173/constraint_provenance_matrix.json
evidence/pass172_173/conflict_register.json
evidence/pass172_173/implementation_traceability.json
evidence/pass172_173/validation_state.json
evidence/pass172_173/recovery_receipt.json
```

Each requirement SHALL retain source pass, variant identity, clause identity, implementation paths, test paths, evidence paths, and terminal status.

## 11. Terminal rule

Pass 172 and Pass 173 cannot reach terminal closure until:

```text
all_discovered_compatible_constraints_retained = true
all_retained_constraints_mapped_to_implementation = true
all_retained_constraints_mapped_to_validation = true
all_true_conflicts_resolved_explicitly = true
contract_source_files_unchanged = true
singleton_vm81_authority_preserved = true
ide_public_api_workflow_authority_preserved = true
stateless_resumption_verified = true
```

The immediate next action is to inventory all variant sources and populate the provenance matrix while leaving both contract files unchanged.