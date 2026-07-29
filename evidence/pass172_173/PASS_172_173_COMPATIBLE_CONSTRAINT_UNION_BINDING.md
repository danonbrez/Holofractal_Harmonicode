# Pass 172–173 compatible-constraint union binding

## Status

```yaml
binding_id: HHS-P172-P173-COMPATIBLE-CONSTRAINT-UNION-V1
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: 3fd4ca088039b1adc0d08a0644d62b979af8997d
active_branch: agent/pass172-173-consolidation-implementation-v5
intended_merge_target: main
status: BOUND_FOR_IMPLEMENTATION
contract_modification_authorized: false
constraint_deletion_authorized: false
constraint_weakening_authorized: false
```

This binding does not rewrite, concatenate, replace, renumber, supersede, or delete either contract. It binds their complete compatible union to shared implementation surfaces.

## Governing rule

```text
ALL COMPATIBLE CONSTRAINTS ARE CUMULATIVE IMPLEMENTATION REQUIREMENTS.
```

For every discovered requirement `r`:

```text
compatible(r, inherited_authority)
⇒ retain(r)
∧ bind_provenance(r)
∧ map_to_implementation(r)
∧ map_to_test(r)
∧ map_to_evidence(r)
∧ require_terminal_closure(r)
```

Identical requirements are implemented once while retaining all provenance. Additive requirements are conjoined. A stricter compatible requirement governs while the weaker requirement remains an inherited minimum. Platform-, profile-, phase-, and authority-scoped clauses coexist at their declared boundary.

A true conflict exists only when two clauses cannot both be satisfied under any explicit profile, platform, phase, authority, or state partition. True conflicts remain source-preserved, receive a machine-readable identity, block terminal closure, and require explicit user-authorized resolution.

## Unified authority constraints

The implementation must preserve simultaneously:

```text
ONE PASS 172 INSTALLATION IMPLEMENTATION AUTHORITY
ONE PASS 173 INDEPENDENT VERIFICATION AND REPAIR AUTHORITY
ONE VM81 RUNTIME AUTHORITY
ONE ADMITTED VM81 COMMIT PATH
ONE HASH72 RECEIPT LINEAGE
ONE HASH216 INSTALLATION-IDENTITY MODEL
ONE CANONICAL PUBLIC API GATEWAY
```

Applications, installer operations, verification tools, deployment tools, and management surfaces are IDE-registered public-API workflow compilations. They are not parallel computation authorities outside the Runtime.

```text
INSTALLER AUTHORITY != RUNTIME AUTHORITY
VERIFIER AUTHORITY != INSTALLER AUTHORITY
IDE WORKFLOW != PARALLEL RUNTIME
```

## Pass 172 cumulative implementation surface

All compatible Pass 172 clauses are mandatory, including:

- non-mutating capability probe before planning or mutation;
- deterministic profile selection and honest degradation;
- verified source acquisition and safe extraction;
- dependency graphs, profile separation, locks, and offline closure;
- isolated Python environments and portable ISO C11 builds;
- native ABI, architecture, artifact, and symbol verification;
- Node/frontend isolation and lock verification;
- LiteRT-LM local GPU, local CPU, external, disabled, degraded, and incompatible states;
- governed model acquisition, verification, quarantine, and import;
- Linux, macOS, Windows, Android/Termux, BSD/POSIX, container, and restricted-cloud adapters;
- POSIX, PowerShell, repository-local, Python, and offline one-command entrypoints;
- transactional staging, activation, update, rollback, repair, and uninstall;
- user-data preservation and explicit destructive-operation authorization;
- privilege plans, port/process safety, and deterministic configuration;
- Hash216 installation identity and append-only Hash72 installation receipts;
- read-only public installation status surfaces;
- local authorized management proposals with expiry and replay protection;
- bounded retries, timeouts, logs, recovery journals, resumable downloads, checksums, and idempotence.

## Pass 173 cumulative verification surface

All compatible Pass 173 clauses are mandatory, including:

- static requirement/dependency traceability;
- clean-environment executed profile and platform matrices;
- independent artifact, identity, and receipt reconstruction;
- fault injection, stable classification, rollback, and deterministic repair;
- redundant evidence for every load-bearing claim;
- native project inventory from the live tree;
- Python and Node dependency closure;
- provider, model, offline, container, Android, path, update, rollback, repair, and uninstall matrices;
- historical evidence preservation and current-state supersession;
- receipt counts derived from executed events;
- independent Hash72 chain verification;
- independent Hash216 installation-identity reconstruction;
- logical replay and full clean-environment replay;
- cross-platform semantic and ABI equivalence;
- security fault injection;
- repair-forward dependency-scoped revalidation;
- one bounded final replay;
- explicit nonterminal classifications for unavailable real hardware or runners.

## Stateless-resumable delivery

Every implementation or verification stage must externalize repository, authoritative base, branch, target, changed files, executed commands, validation results, remaining checks, environment state, blocker, exact next action, timeout, and fallback before a long-running or failure-prone step.

No task may depend on an open process, private scratch state, conversation memory, or indefinite polling.

## Integration policy

“Merge” means integration into common authoritative implementation surfaces, not concatenation of contract prose. The implementation must prefer shared primitives, shared transaction machinery, shared canonical serialization, shared receipt builders, shared capability checks, and profile/platform adapters over duplicate authorities.

No source contract file may be edited by this task.
