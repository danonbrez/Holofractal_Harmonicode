# Holofractal Harmonicode (HHS)

HHS is a deterministic, receipt-governed programming environment that combines Harmonicode source semantics, VM81 execution and admission, Hash72 receipt lineage, Hash216 ordered identity, native C ABI surfaces, Python runtime control, backend APIs, visual development, replay, persistence, and governed multimodal tooling.

## Current authoritative repository state

The repository is a **working transitional hybrid**, not a scaffold.

| Layer | Current repository state |
|---|---|
| Pass 159 toolchain | VM81 + Hash216 Harmonicode interpreter and C11 native compiler evidence is closed on authoritative `main`. |
| Pass 190 | Iterations 1–7 are present. Iteration 7 is verified for durable workers, dependency scheduling, deterministic claims, cancellation, retry, stale-worker recovery, and receipt-bound execution of registered pure operations. |
| Pass 190 registry | 42 governed operations: 10 inherited native ABI operations and 32 exact VM81-authority fallback operations. |
| Pass 191 | The universal Genesis-to-runtime repository-hydration contract is frozen on `main`. Contract presence does not by itself claim full Pass 191 implementation or repository-wide verification. |
| Visual environment | `bash start.sh` launches the integrated HHS visual development assistant through `hhs_backend.visual_server:app`. |
| Deployment target | DigitalOcean/systemd deployment assets are repository-native for Pass 189 Iterations 1–4, the Pass 190 service and worker path, and the Pass 196 integrated environment. Vercel is not part of those acceptance paths. |

The latest completed Pass 190 layer intentionally does **not** claim external provider execution, arbitrary subprocess execution, mutating target execution, multi-host consensus, final Pass 190 completion, or live DigitalOcean production acceptance.

## Authority model

```text
input
→ parser and source preservation
→ symbolic or macro expansion
→ typed state proposal
→ VM81 admission
→ kernel and invariant audit
→ LOCKED or QUARANTINED gate
→ Hash72 receipt
→ Hash216 identity/topology witness
→ replay, persistence, API, SDK, and visual projection
```

Binding rules:

- VM81 is the semantic execution, admission, and authoritative state-transition substrate.
- Hash72 is the canonical receipt and causal-lineage authority.
- Hash216 preserves ordered identity, indexing, topology, and historical evidence.
- Canonical kernel arithmetic is exact; floating-point values may be display, timing, benchmark, or calibration witnesses but do not silently replace exact state.
- Ordered products such as `xy` and `yx` must not be collapsed unless an applicable law proves equivalence.
- Every mutation must be explicit, audited, receipt-bound, and replay-verifiable.
- Language-model output is a proposal or capability result, not canonical state merely because inference completed.

## Repository layout

The repository currently preserves root-level compatibility modules while canonical implementations increasingly live in structured package paths.

| Path | Responsibility |
|---|---|
| `hhs_runtime/` | Canonical runtime substrate, core sandbox, kernel resolution, C runtime, testing, and execution helpers |
| `hhs_python/` | Python runtime controller and ctypes bridge surfaces |
| `hhs_backend/` | FastAPI lifecycle, orchestration, assistant, routes, WebSockets, runtime services |
| `hhs_graph/` | Receipt and multimodal graph topology |
| `hhs_storage/` | Durable state and persistence primitives |
| `native_projects/` | Pass-scoped native implementations, contracts, validation, deployment, and restart records |
| `hhs_gui/` and `applications/` | Visual runtime applications and user-facing development surfaces |
| `docs/` | Architecture, pass contracts, explanatory papers, deployment, and operational documentation |
| root modules | Compatibility imports and historical entry points; new canonical logic should not be added here unless the change is intentionally a compatibility repair |

Example compatibility path:

```text
hhs_general_runtime_layer_v1.py
→ hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1
```

## Current Pass 190 operation fabric

The active implemented operation-fabric surface lives under:

```text
native_projects/hhs_pass190_operation_fabric/
```

Iteration 7 execution path:

```text
registered pure operation
→ durable execution job
→ dependency and schedule admission
→ capability-matched worker
→ Hash72 execution claim
→ exact target evaluation
→ one outer VM81 admission
→ one Hash72 receipt and event
→ completed, retry-wait, failed, or cancelled job state
```

Key properties:

- one authoritative SQLite state for resources, workers, jobs, leases, fences, receipts, and events;
- exact integer nanosecond coordinates for schedules, heartbeats, retries, leases, starts, and completion;
- deterministic job selection by highest priority and then lexicographically smallest job ID;
- acyclic same-workspace dependency graphs;
- one running job per worker;
- receipt-bound pure-operation execution;
- bounded retry and stale-worker recovery;
- generated Python and TypeScript SDK parity;
- visual authority and OpenAPI exposure;
- shared DigitalOcean service state for API and worker processes.

### Validate Pass 190 Iteration 7

```bash
cd native_projects/hhs_pass190_operation_fabric
make validate
```

The validation target builds and tests the native ABI, runs Iterations 1–7 tests, checks compilation, rejects private `eval`/`exec`, checks generated SDKs and bindings, verifies GUI surfaces, verifies deployment assets, and runs iteration-specific evidence checks.

### Pass 190 runtime route

Iteration 7 adds:

```text
GET /api/pass190/execution-runtime
```

The Pass 190 service is designed to run on `127.0.0.1:8190` behind the repository deployment boundary. The API and worker services share:

```text
/var/lib/hhs/pass190-authority.sqlite3
```

## DigitalOcean deployment operations

The canonical installation and operations runbook for the Pass 189 DigitalOcean stack is:

[`docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`](docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md)

It documents:

- Ubuntu host preparation and repository installation;
- Pass 189 systemd dependency ordering and nginx TLS routing;
- local and public verification;
- controlled upgrades and restart procedures;
- SQLite and filesystem backups;
- restore and rollback;
- security maintenance, logs, troubleshooting, and incident isolation;
- routine daily, weekly, and monthly maintenance;
- the default `8190` collision between Pass 189 Iteration 2 and Pass 190.

Before co-hosting multiple pass services, assign and record a non-conflicting loopback port plan. Pass 196 uses `127.0.0.1:8080`; Pass 189 uses `8189–8192`; Pass 190 currently defaults to `8190` and therefore requires relocation or a separate host when Pass 189 Iteration 2 is enabled.

## Integrated visual environment

### Prerequisites

- Python 3.11+
- GCC or Clang
- GNU Make
- Node.js 22+
- accelerator and driver support for the selected local model-provider profile

### Start

```bash
git clone https://github.com/danonbrez/Holofractal_Harmonicode.git
cd Holofractal_Harmonicode
python -m pip install -r requirements.txt
bash start.sh
```

Open:

```text
http://localhost:8080/
```

The default composition provides the visual development assistant, registered-object workspace, nested inspectors, governed HHS tools, provider and authority diagnostics, and degraded startup when the model provider is unavailable unless strict startup is enabled.

The former root JSON status remains available through:

```text
GET /api/system/status
```

## Harmonicode program and macro surfaces

The repository contains:

- `.hhsprog` executable program format;
- `.hhsrun` receipt-bearing run results;
- `run`, `verify`, `inspect`, and `demo` CLI commands;
- exact integer and rational runtime operations;
- algebra-native macros;
- nested macro expansion;
- symbolic commitments;
- Hash72 expansion and call receipts;
- replay verification.

Core files:

```text
terminal_hhsprog_v5_macro_algebra.py
hhs_program_format_and_cli_v1.py
hhs_receipt_replay_verifier_v1.py
hhs_general_runtime_layer_v1.py
```

Macro execution model:

```text
macro source
→ canonical symbolic macro
→ parameter binding
→ nested expansion
→ symbolic commit
→ AuditedRunner receipt
→ replayable Hash72 chain
```

## Pass 191

The normative contract is:

[`docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md`](docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md)

Its target is:

```text
one repository
→ one complete historical lineage
→ one canonical object graph
→ one canonical operation registry
→ one universal invariant envelope
→ one VM81 admission authority
→ one Hash72 commit chain
→ one Hash216 identity topology
→ many consistent user and machine surfaces
```

The companion educational manuscript is:

[`docs/pass191/HHS_DYADIC_QUARTIC_PHASE_LATTICE_AND_HARMONICODE_EXPLANATORY_ESSAYS.md`](docs/pass191/HHS_DYADIC_QUARTIC_PHASE_LATTICE_AND_HARMONICODE_EXPLANATORY_ESSAYS.md)

It explains the dyadic–quartic phase lattice, critical resonance, integer and rational phase states, Fibonacci/plastic/Collatz relations, quadratic reciprocity, receipts, repository architecture, and the Harmonicode language in educational natural language.

## Canonical documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — ownership boundaries, canonical paths, current pass layering, and anti-drift rules
- [`RUNTIME_FLOW.md`](RUNTIME_FLOW.md) — end-to-end execution, receipt, replay, worker, API, and visual projection flow
- [`GLOSSARY.md`](GLOSSARY.md) — stable definitions for the principal HHS terms
- [`AGENTS.md`](AGENTS.md) — repository navigation and implementation rules
- [`docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`](docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md) — DigitalOcean installation, service operation, backup, restore, rollback, security, troubleshooting, and maintenance
- [`HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING.md`](HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING.md) — current verified operation-fabric contract

## Baseline validation

Run from the repository root:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

Run Pass 190 validation separately:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

A path or environment failure should be repaired at the adapter or deployment layer. Invariant checks, receipt continuity, ordered identity, and replay requirements must not be weakened to make a test pass.
