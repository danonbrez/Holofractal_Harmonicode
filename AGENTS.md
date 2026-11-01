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

## 1A. Unified specification and completion contract

Read [HHS unified specification completion and non-reduction contract](contracts/system/HHS_UNIFIED_SPECIFICATION_COMPLETION_AND_NONREDUCTION_V1.md) before narrowing a requested implementation to an existing service, proof, test, or named pass. Treat all repository artifacts as cumulative system components; incomplete discovery or implementation is not a reason to stop. Preserve all pre-beta-freeze lineage. Never bypass validation; investigate both the underlying defect and missed workflow coverage.

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
