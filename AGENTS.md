# AGENTS.md — HHS Repository Navigation and Execution Contract

This repository hosts the Holofractal Harmonicode general programming environment. Work must preserve the single VM81, Hash72, Hash216, exact-algebra, receipt, and replay authority path.

## 1. Read first

Before changing runtime behavior, read:

1. [`README.md`](README.md) — current repository state and primary entry points
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — canonical ownership boundaries and anti-drift rules
3. [`RUNTIME_FLOW.md`](RUNTIME_FLOW.md) — execution, receipt, replay, worker, API, and visual flows
4. [`GLOSSARY.md`](GLOSSARY.md) — stable terminology
5. the applicable pass contract and restart record

Current pass-specific anchors:

```text
HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING.md
docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md
docs/pass191/HHS_DYADIC_QUARTIC_PHASE_LATTICE_AND_HARMONICODE_EXPLANATORY_ESSAYS.md
```

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
