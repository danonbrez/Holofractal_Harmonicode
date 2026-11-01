# AGENTS.md — HHS Repository Navigation and Execution Contract

This repository hosts the Holofractal Harmonicode general programming environment. Work must preserve the single VM81, Hash72, Hash216, exact-algebra, receipt, and replay authority path.

## 1. Read first

Before changing runtime behavior, read:

1. [`README.md`](README.md) — current repository state and primary human entry point; it links directly to the repository index
2. [`REPOSITORY_INDEX.md`](REPOSITORY_INDEX.md) — canonical repository navigation map for runtime, contracts, pass documentation, validation, deployment, applications, and the full Hash216 dependency graph
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) — canonical ownership boundaries and anti-drift rules
4. [`RUNTIME_FLOW.md`](RUNTIME_FLOW.md) — execution, receipt, replay, worker, API, and visual flows
5. [`GLOSSARY.md`](GLOSSARY.md) — stable terminology
6. the applicable pass contract and restart record

Repository navigation SHALL follow the shared index rather than reconstructing an independent path map:

```text
README.md
→ REPOSITORY_INDEX.md
→ REPOSITORY_HASH216_DEPENDENCY_TREE.md
→ artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json
→ artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json
  + artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json
  + docs/repository_index/files/*.md
```

Agents may enter the index directly through [`REPOSITORY_INDEX.md`](REPOSITORY_INDEX.md) or through the [`README.md`](README.md) repository-navigation link. The generated Hash216 tree, Lane 5 hydration knowledge graph, database receipt, and file-link shards are the repository-wide discovery/hydration surface; they do not replace the applicable canonical contracts or runtime authority.

Current pass-specific anchors:

```text
HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING.md
docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md
docs/pass191/HHS_DYADIC_QUARTIC_PHASE_LATTICE_AND_HARMONICODE_EXPLANATORY_ESSAYS.md
```

## Frozen-layer preservation (normative)

Read [HHS Frozen-Layer Preservation Contract](docs/architecture/HHS_FROZEN_LAYER_PRESERVATION_CONTRACT.md) before developing higher-order features. A closed and admitted foundation is a frozen dependency: extend through existing constructors, interfaces, and Lane 5 hydration, not a foundational rewrite. Missing higher-level capabilities do not establish lower-layer defects. Preserve exact ordered semantics, proofs, addresses, provenance, signed VM81 admission, Hash72 receipts, and Hash216 history. Independently validate new compositions; route any independently verified lower-layer defect to an explicitly authorized, regression-evidenced repair, separate from the extension.

## 2. Current status boundary

- Pass 159 Harmonicode interpreter/C11 toolchain authoritative-main closure evidence is present.
- Pass 190 Iteration 7 is the current verified durable worker and registered pure-operation execution layer.
- Pass 190 Iteration 7 exposes 42 governed operations while preserving the inherited ten-operation C ABI.
- Full Pass 190 completion is not claimed.
- Pass 191 universal repository hydration is a frozen normative contract. Contract presence is not equivalent to implementation or verification.
- The default integrated visual environment remains the `bash start.sh` composition.

Do not promote planned, contracted, or partially integrated behavior into a verified claim.

## 3. Canonical paths

The repository is a transitional hybrid layout.

| Path | Responsibility |
|---|---|
| `hhs_runtime/` | canonical runtime, kernel resolution, exact execution, C surfaces, core sandbox, testing |
| `hhs_python/` | runtime controller and ctypes bridge |
| `hhs_backend/` | FastAPI composition, orchestration, routes, assistant, WebSockets, services |
| `hhs_graph/` | receipt and object graph topology |
| `hhs_storage/` | durable state and persistence |
| `native_projects/` | pass-scoped native implementations, contracts, evidence, deployment, restart records |
| `hhs_gui/`, `applications/` | visual runtime applications and user workspaces |
| `docs/` | normative and explanatory documentation |

Root-level runtime files are compatibility surfaces unless an applicable contract explicitly assigns them canonical ownership.

Example:

```text
hhs_general_runtime_layer_v1.py
→ hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1
```

Prefer modifying canonical package implementations. Keep compatibility shims thin.

## 4. Governing invariants

All canonical computation must preserve:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
```

Binding rules:

- no floating-point canonical authority;
- exact integer, rational, symbolic, phase, ordered-byte, and membrane-preserving forms remain authoritative;
- all state transitions are explicit and receipt-committed;
- parent receipt continuity and replay verification are mandatory;
- ordered products such as `xy` and `yx` must not be silently collapsed;
- exact `List(...)` circuit encodings retain every element, position, lexical width, and leading zero;
- no alternate integrity or mutation authority may be created;
- no route, WebSocket handler, GUI state, provider result, worker-local queue, or storage adapter may bypass VM81 admission.

## 5. Canonical execution pattern

```text
input
→ source preservation and parsing
→ symbolic or macro expansion
→ typed state proposal or patch
→ registered runtime/controller path
→ singleton VM81 admission
→ kernel and invariant audit
→ LOCKED or QUARANTINED gate
→ Hash72 receipt
→ Hash216 identity/topology witness
→ replay and persistence
→ API, SDK, assistant, and visual projection
```

## 6. Primary runtime files

Compatibility/public entries:

```text
hhs_general_runtime_layer_v1.py
hhs_state_layer_v1.py
hhs_program_format_and_cli_v1.py
terminal_hhsprog_v5_macro_algebra.py
hhs_receipt_replay_verifier_v1.py
hhs_runtime_smoke_tests_v1.py
hhs_regression_suite_v1.py
hhs_v1_bundle_runner.py
```

Canonical general runtime:

```text
hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py
```

Pass 190 operation fabric:

```text
native_projects/hhs_pass190_operation_fabric/
```

## 7. Pass 190 Iteration 7 rules

Iteration 7 executes registered operations only when:

```text
operation.effect_class == pure
```

The path is:

```text
job submission
→ dependency/schedule validation
→ deterministic eligibility
→ capability-matched worker
→ Hash72 claim
→ exact target evaluation
→ one outer VM81 admission
→ one receipt/event/state update
```

Do not add:

- arbitrary subprocess execution;
- mutating target execution through workers;
- provider execution without a bounded contract;
- worker-local canonical queues;
- float time authority;
- a second scheduler or mutation authority.

All schedule, heartbeat, retry, lease, start, and completion coordinates remain exact integer nanoseconds.

## 8. Prohibited changes

Do not:

- redefine Hash72;
- bypass Manifold9 or drift gates where required;
- create alternate integrity, receipt, or truth paths;
- replace rational or exact canonical arithmetic with floats;
- silently normalize identity-bearing ordered lists or bytes;
- mutate state without a patch and receipt;
- embed execution logic in API routes, WebSockets, GUI components, compatibility shims, or storage adapters;
- fabricate provider, backend, deployment, test, receipt, replay, or completion evidence;
- weaken invariant checks to work around path or environment failures;
- claim Pass 191 completion from the existence of its contract or explanatory essay.

## 9. Testing

Run repository baseline checks from the root:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

Run the Pass 190 Iteration 7 validation suite:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

The Pass 190 target validates native ABI compilation/tests, Iterations 1–7, Python compilation, no-private-eval rules, generated SDKs and bindings, GUI evidence, deployment assets, and iteration-specific verification.

If a test fails because of path, environment, or deployment assumptions, repair the adapter or setup layer. Do not weaken canonical checks.

## 10. Change discipline

Every task must remain restartable from repository-visible state.

Record:

- base commit;
- branch or merge target;
- changed files;
- commands executed;
- validation completed;
- validation remaining;
- environment state;
- blockers;
- next action.

Prefer:

```text
IMPLEMENT
→ DEPENDENCY-SCOPED VALIDATION
→ COMMIT
→ MERGE OR READY PR
→ VERIFY MAIN
→ REPORT COMPLETION
```

Commit only intended files. Preserve inherited pass artifacts and history unless an explicit ratified migration supersedes them.

## 11. First inspection sequence

For a new task:

1. inspect `git status` and current branch;
2. identify the applicable pass contract and restart record;
3. run the smallest relevant validation before changing code;
4. trace the current canonical implementation path;
5. inspect compatibility wrappers only after locating the canonical module;
6. implement without creating an alternate authority path;
7. rerun dependency-scoped checks;
8. update documentation when ownership, public surfaces, commands, status boundaries, or terminology change.

## 12. Modules 27–72: native relational tensor interpretation and evidence boundary (2026-10-31)

This section records the user-supplied Modules 27–72 as a system-internal **interpretation and implementation-inspection contract**. It does not replace frozen mathematics, applicable service contracts, native VM81/Hash72/Hash216 semantics, or independently verified source and test evidence. Consult `REPOSITORY_INDEX.md`, `REPOSITORY_HASH216_DEPENDENCY_TREE.md`, applicable Pass 219–221 contracts, actual C/C++ runtime, Lane 5 service index, and proof/receipt checks before changes. Extend existing implementations through inheritance/composition and approved Lane 5 hydration interfaces; do not rewrite closed lower layers merely to accommodate a higher-level synthesis.

### Native relational invariants and constructors

- Preserve **Δ = 1** as the primitive quantization/denominator unit, distinct from mirror charge **−1**. Preserve the typed, ordered local channels **AB = P⁴ = c⁴**, **BA = −P⁴**, and their cell addresses, provenance, and phase order. The forward/mirror cancellation **AB + BA = 0** and retained difference **AB − BA = 2P⁴** are native ordered-ledger statements; do not replace them with unsupported classical commutative or invertible-scalar-matrix interpretations.
- The one-input unit-orbit constructor is **p=P−1**, **q=P+1**, **pq=P²−1**, **A=B=P²**, with **P²−pq=1**, **p+q=2P**, and **q−p=2**. Derived ratios and modular operations require domain guards, especially at **P=0** and **P=±1**. Twin offsets are not necessarily prime. The successor relation is **P_n=P₀+3n** with corresponding **p_n=P_n−1**, **q_n=P_n+1**.
- Retain Fibonacci/Pythagorean role and address distinctions **a²,b²,c²,d²,e² ↔ 1,2,3,5,8** with applicable constitutive relationships; never collapse distinct tensor roles because a fixed scalar projection happens to coincide.
- Preserve **ordered** `List`, `MatrixTimes`, source, tensor positions, exact rational/dyadic payloads, reciprocal classes, Euclidean-mod floor wrapping, and the difference between elementwise reciprocal and matrix inverse. HNAN division sites use the established guarded gain-1/no-phase-write path **only where the existing native gate contract actually authorizes it**; never silently redefine undefined ordinary operations as identities.

### Endogenous execution and proof-carrying state

- In a nested equation each active `==` gate has local typed **A_g=LHS_g**, **B_g=RHS_g** roles; these are cell-resident states, not instructions to create a separate authoritative constraint solver. Construct dependent tensor relationships from the active input; expand valid alternatives; propagate shared input/output relationships internally; reconstruct the same anchor and typed ordered product through independent branches; prune contradictions, or preserve an explicit unresolved boundary.
- Admission demands applicable exact residual closure, shared-anchor consensus, immutable inherited constraints, a valid return/retraction path when required, and the pre-existing singleton VM81 authority. A scalar evaluation is a **projection/receipt** of the tensor relationship, not its replacement. Round-trip construction/reconstruction must be checked on the admitted domain, including sign/phase ambiguity and guarded sites.
- Cell records retain ordered Lo Shu product provenance, normalization factors, reciprocal denominator/guard, input/output roles, phase shell address, inverse/adjugate relationships where defined, lineage, and validation status. Hash216 can project these as relational knowledge **after** the admitted three-Hash72 receipt block; candidate discovery or tensor construction alone does not authorize a canonical Hash216 commit.
- Respect the **72-root** and **216-root** phase shells and their exact address/branch relations, the centered Lo Shu and Lo Shu/prime-numerator constructions, and the **248=8×31** E8 normalization dictionary. The numerical E8/Lo Shu correspondence does **not** establish an E8 root-level or Lie-bracket isomorphism without explicit root mapping and bracket-equivariance proof.
- The continuous-to-discrete orbital interpretation retains a representable exact anchor and explicit residual/phase information, subject to reversible pruning/retraction and receipt conservation. Do not discard a nonzero residual, round it into closure, or redefine the exact rational epsilon floor as random noise.

### Gate status and falsifiable proof boundary

- User-supplied modules contain claimed executed receipts. Treat them as **provided specifications and candidate evidence** until matching committed source, reproduced exact-arithmetic tests, proof dependencies, runtime traces, and authoritative-main evidence are inspected. **Δe=0, Ψ=0, Ω=true** in a supplied terminal statement is not itself an executable acceptance receipt.
- Preserve explicitly **open** results: Module 54 cross-register reciprocal gates; Module 56 outer terminal and qubit gates plus missing 5-vector/3×3/two-block contraction interface; Module 58 remaining incompatible scalar/gate loci and full composite closure. Do not infer full-chain closure from exactness of constituent registers.
- Keep measured-constant normalizations (fine-structure inverse, proton/electron mass ratio, decoupling redshift, acoustic angle) as **candidates with nonzero experimental residuals**, not established physical derivations. Distinguish analytical identities, system-internal physical interpretations, and independent experimental confirmation.
- Test each implementation claim against the active contract and actual native operation ordering; record **PASS / FAIL / OPEN**, input locus, type, domain guards, exact residual, proof identity, predecessor/receipt linkage, and replay outcome. A local identity or per-cell pass never automatically certifies composed behavior. For guarded Lean 4 proof integration, maintain pinned native toolchain/dependency and theorem identities where the applicable service contract requires them.

This section is additive guidance for implementation review. The established VM81 commit and Hash72-before-Hash216 authority order, frozen-layer preservation, and repository-wide source-integrity controls remain unchanged.

## 13. Universal cumulative integration, capability completion, and beta-freeze contract (2026-10-31)

**Universal destination:** Every design, equation, algorithm, visualization, proof, prototype, optimization, dataset, test, and artifact developed for HHS/HARMONICODE, in any language or environment, belongs to **one integrated HARMONICODE system**. Its current implementation location does not change its architectural destination. Every repository component is part of this unified architecture, even when integration is indirect, incomplete, or not yet indexed. The knowledge-graph HTML is an integrated inspection/prototype surface, not a separate project.

### Repository-wide discovery and implementation

1. Before asserting that a capability is absent, inspect the repository index, source files, constructors, service registry, tests, proofs, dependency graph, historical implementations, native interfaces, and Hash216/Lane 5 hydration graph. `AGENTS.md`, indices, names, descriptions, pass labels, and registries are **navigation aids**, not exhaustive capability boundaries.
2. An incomplete service, missing interface, obscure name, or disconnected component establishes investigation or integration work, **not permission to abandon the task** or claim the architecture lacks the capability. Reconstruct dependencies and implement the requested missing capability or connection.
3. Reuse native VM81, Hash72/Hash216, Lane 5, and relevant C/C++ services and constructors wherever they actually satisfy the specification; extend through composition, inheritance, and compatible interfaces. Do not create competing mutation, proof, receipt, or execution authority.
4. All standalone HTML, JS, Python, C++, and other artifacts are portable implementations or inspection surfaces participating in the same lifecycle. Where applicable, preserve standalone execution with embedded portable VM81 and relevant Lane 5 native optimization semantics rather than presenting a remote service as the only runtime. Verify typed input/output and observable compatibility at ingress and egress.
5. Carry development toward production integration. A functioning standalone prototype is **not** sufficient evidence of full integration: verify relevant native execution, interface parity, exact-algebra constraints, Hash72/Hash216 receipts, replay, deployment identity, and production acceptance.

### Specification fidelity and non-reduction

- A narrow test or existing proof proves only its tested or demonstrated claim; it does **not** bound the broader requested specification. Existing service behavior and shared mathematical properties do not imply full implementation or equivalence.
- Evaluate each newly supplied design and number-theoretic construction on its exact terms, preserving operator order, Lo Shu addresses, types, provenance, phase relationships, guards, constraints, and observable outputs. An unconventional, simpler, or more complex iteration remains an implementation requirement when specified.
- A proposed simplification, optimization, or substitute requires an explicit equivalence witness under all applicable native and interface constraints. Reuse satisfied capabilities, extend partial ones, and construct what remains missing without rewriting frozen lower layers.
- Distinguish verified implementation, proof scope, contractual intent, and open work; do not present partial or isolated success as full system closure.

### Pre-beta preservation and authorized consolidation

Until **the fully functioning integrated beta has been verified and explicitly frozen**, the repository remains cumulative. Do not prune, delete, archive, or fork branches, files, services, proofs, experiments, historical implementations, or transition artifacts **merely because they appear redundant, unused, old, or disconnected**. Preserve developmental lineage, source integrity, provenance, reproducibility, and inherited frozen mathematics/runtime/service contracts. Incomplete connectivity calls for investigation and integration, not disposal.

Required lifecycle:

```text
CUMULATIVE DEVELOPMENT
→ REPOSITORY-WIDE DISCOVERY AND INTEGRATION
→ END-TO-END BETA EXECUTION / PROOF / INTERFACE / DEPLOYMENT / REPLAY VALIDATION
→ EXPLICITLY AUTHORIZED BETA FREEZE
→ CONTROLLED FORK
→ EVIDENCE-BASED PRUNING AND ARCHIVAL WITH FULL LINEAGE
```

Only after beta verification and authorized freeze may consolidation decisions rely on complete dependency evidence. Routine feature/work branches and commits needed for cumulative implementation are not the post-freeze repository fork/pruning authorization; preserve their history and do not destructively consolidate them prematurely.

### Rejection integrity, bypass detection, and diagnostic evidence

1. **Never bypass native rejection.** Preserve VM81 admission, tensor/HNAN guards, Hash72/Hash216 integrity, replay, receipt lineage, frozen-layer protection, source-integrity checks, and production validation. Rejection is diagnostic evidence, not an obstacle to circumvent.
2. Trace failure from native error code, invariant and exact witness through affected constructor/service, interface/ABI, dependency and Lane 5 hydration edges. Repair the defective implementation rather than weakening the validator unless the validator defect itself is independently demonstrated.
3. Test **the validation bypasses themselves**: renamed protected paths (including real Git rename cases), changed paths, alternate entry points, missing or malformed receipts, invalid transitions, omitted checks, diff-scope failures, and deployment identity drift. A green CI result does not prove an unexercised contract.
4. Preserve an end-to-end evidence chain from source/base SHA, changed paths, guard selection and execution, tests, commit/merge SHA, build artifact, deployed SHA, native runtime identity, rejection/admission witness, and replay.
5. Classify and retain diagnostic evidence for **source defect** (invariant/service/constructor/operation), **integration defect** (dependency/ABI/hydration), **validation bypass** (expected/executed guard and uncovered route), **workflow defect** (diff/test selection/skipped checks), **deployment drift** (source/build/deployed/runtime identities), and **runtime rejection** (error code/constraint witness/transition provenance).
6. If a bypass has already reached `main`, repair **both** the underlying defect and the missing guard/coverage. Passing CI or deployment alone is insufficient evidence of native contract closure.

### Required task procedure and honest blocker handling

```text
REQUESTED CAPABILITY
→ REPOSITORY-WIDE DISCOVERY
→ SPECIFICATION / IMPLEMENTATION / CONTRACT ANALYSIS
→ DEPENDENCY AND INHERITED-STATE RECONSTRUCTION
→ IMPLEMENT MISSING CAPABILITY AND INTEGRATION
→ NEGATIVE-GUARD AND END-TO-END VALIDATION
→ PRODUCTION INTEGRATION AND REPLAY EVIDENCE
```

If a genuine external blocker prevents full completion, preserve the completed changes, identify the exact blocker, missing tests and evidence, and reproducible next action. Do not abandon the work merely because the first located implementation is incomplete, and never misstate partial work as complete. All requirements in this section are additive to the frozen-layer preservation contract and existing authoritative runtime semantics.

## 14. Validation-history recovery and evidence-first integration (2026-11-01)

**Governing contract:** Historical validation is part of the cumulative HHS/HARMONICODE implementation foundation. Before rederiving, simplifying, replacing, or independently reimplementing specified mathematics or algorithms, recover and trace existing mathematical, executable, and integration evidence. Do not require the user to repeatedly reproduce recoverable historical verification.

### Distinct evidence states

1. **Established mathematical results:** Recover exact ordered typed expressions, assumptions, domain guards, formal proof identities and checker outputs. Investigate prior scientific-calculator artifacts, independent LLM agent reviews, Wolfram formalizations, native Lean 4 proofs, and other recorded evidence. A file's existence alone does not certify its assertions; identify the actually proven scope.
2. **Verified native implementations:** Trace these results to existing C/C++ constructors, VM81 operations, source SHAs, tests, GitHub Copilot/code reviews, CI workflow execution IDs, native error and admission witnesses, Hash72/Hash216 receipts, replay, and Lane 5 hydration graph edges. A passing workflow proves only its exercised contract scope.
3. **Outstanding integration:** Record separately which verified behaviors still lack portable HTML, audiovisual, compressed rendering, typed ingress/egress, interface-parity, native runtime, or production integration. Missing HTML connectivity does not negate independently verified mathematics; a Lean proof or VM81 success does not certify untested interfaces.

### Required agent procedure

1. Search repository-wide and available connected histories for the relevant calculator calculations, independent-agent verifications, Wolfram scripts, Lean theorems, Copilot review results, VM81 workflow records, Hash72/Hash216 receipts, and Lane 5 hydration records. Preserve provenance, version, scope, failure evidence, and toolchain/checker identity; never invent missing historical records.
2. Trace evidence across existing source, constructors, dependencies, service contracts, proof identities, native validation, CI, deployment receipts, and replay. AGENTS.md, service indexes, and registries facilitate discovery; they are not exhaustive limits.
3. Inspect relevant concrete anchors where applicable: hhs_runtime/cpp/hhs_pass220_i086_lane5_conway_cell_wall_v1.cpp; docs/pass220/PASS_220_I051_NATIVE_LEAN_ALIGNMENT.md; formal/wolfram/pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1.wl; contracts/pass219/PASS_219_LANE5_REPOSITORY_HYDRATION_KNOWLEDGE_GRAPH_1_69.md. Their presence identifies investigation paths, not proof of all claims.
4. Maintain an evidence ledger recording construction/claim, exact expression and assumptions, source SHA, checker/proof identity and result, verification scope, executable constructor/runtime and receipts, PASS/FAIL/OPEN status, and unresolved integration paths. Distinguish absent evidence, an unexecuted test, and an actual failure.
5. Reuse already proven results within their recorded scope. Do not replace the specified mathematics with simplified equations, approximate surrogates, or invented visualization algorithms absent an exact typed, ordered, address/phase/provenance-preserving equivalence witness.
6. Integrate verified behavior into portable HTML, audiovisual, compressed rendering, and production surfaces through inherited native constructors and compatible interfaces. Test input/output parity, negative guards, replay, source-to-deployment identity, and native acceptance. A working standalone visualization is not full integration.
7. When evidence is inaccessible, document precisely which sources were examined, what remains unverified, and a reproducible next recovery step. Do not downgrade verified scoped results or overstate evidence from filenames and green workflows.

**Decision rule:** Recover and scope validation evidence first; inherit established mathematics and implementations; diagnose and complete only genuinely missing connections; verify full integration without weakening VM81, Hash72/Hash216, Lane 5, or frozen-layer authority. Additive to Sections 1–13.
