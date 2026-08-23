# Holofractal Harmonicode (HHS)

HHS is one cumulative deterministic, receipt-governed programming and runtime environment. It combines a pre-pass state-change/kernel-protection foundation, exact Harmonicode semantics, singleton VM81/kernel admission, Hash72 receipt lineage, Hash216 ordered archival/indexing identity, native and Python runtime surfaces, hydration/continuation systems, backend APIs, visual development, replay, persistence, acceleration, and governed multimodal/agent tooling.

The numbered pass system is additive. It does not define a collection of independent runtimes.

## Current repository state

The repository is a **working transitional hybrid with active unmerged continuation branches**.

Current observed state for this documentation alignment:

| Layer | Repository state |
|---|---|
| Pre-pass foundation | Predates Pass 001. System-wide architecture now explicitly records its kernel-protection, error-correction, cross-format, path/time/noncommutative, rollback, and optimization boundaries. This clarification is documentation-only and is not a new pass. |
| Authoritative `main` | `3c926453d65b71a6d1789e06b748544f5f2bd228`. Its runtime parent is Pass 219B I6 merge `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`; the subsequent main commit adds creative-writing content rather than a new runtime closure. |
| Pass 219B I7 | PR #319, validated head `6df75bc39fd7c58108b8cf7aee3758341fe345a5`, open and unmerged. Exact selective projection optimization; zero new canonical mutation/Hash72 authority. |
| Pass 220 | PR #320, head `d0fb6165bf8249175566c934820eecf8e93bdacc`, draft and unmerged. Native Linux VM/bootstrap work remains `NON_PROMOTIONAL_PREIMPLEMENTATION` until terminal Pass 219 closure. |
| Post-220 Deployment Target 1 | Authenticated OpenAPI remote-agent object workspace is a binding downstream target, not an implemented/accepted production service. |
| Universal Knowledge Economy network | PR #321, validated contract head `d4146f4553920a1776962400a4df4e64c994f45e`, draft and unmerged. It specifies downstream P2P/resource/federation/lineage architecture without claiming network implementation. |

Do not infer Pass 219 terminal closure, Pass 220 implementation admission, Deployment Target 1 acceptance, or production UKE federation from the existence of these contracts/branches.

## Foundational architecture

The system hierarchy is:

```text
PRE-PASS STATE-CHANGE / KERNEL-PROTECTION ENVIRONMENT
        ↓
SINGLETON VM81 / KERNEL ADMISSION AND COMMIT AUTHORITY
        ↓
HASH72 ADMITTED RECEIPT / STATE LINEAGE
        ↓
NUMBERED PASS SYSTEM
        ↓
HASH216 / HYDRATION / CACHE / GPU / AGENT / IDE / NETWORK OPTIMIZATIONS
```

The pre-pass foundation is **not Pass 000** and is not owned by a later numbered pass.

Its architectural role is primarily:

```text
kernel protection
+ error correction
+ state-continuity enforcement
+ multimodal cross-validation
+ path/time/order-sensitive transition constraints
+ lightweight prediction / optimization
+ automatic rollback on required disagreement
```

It is not accurately described as one obvious security package. HHS also has explicit security mechanisms—hashing, signatures, authentication, capabilities, PQC/network profiles, isolation, and receipts—but those are a separate real layer rather than a substitute for the pre-pass state-change substrate.

The detailed clarification is:

[`docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md`](docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md)

## Cross-format state law

Multiple required authoritative representations may encode the same raw state differently, but they may not disagree about that state.

```text
for every required authoritative modality m:
Normalize_m(View_m) = canonical_raw_state
```

This is exact equality enforcement, not consensus voting.

```text
required representation disagreement
→ closure failure
→ no canonical commit
→ retain / restore last fully closed state
```

A mode, backend, model, cache, GPU, API, or pass cannot select one disagreeing representation as the new truth.

## Authority model

At the system level:

```text
input / candidate
→ exact source and raw-state identity preservation
→ applicable parsing / typing / capability / policy checks
→ pre-pass path/time/multimodal/noncommutative compatibility
→ required cross-format equality and correction closure
→ singleton VM81/kernel admission
→ exact inherited invariant closure
→ LOCKED / CORRECTED / RECOVERED / REJECTED / QUARANTINED
→ Hash72 receipt commitment if admitted
→ Hash216 archival / indexing / topology witness
→ replay / persistence
→ native / API / SDK / assistant / visual projection
```

Binding rules:

- VM81/kernel remains the singleton semantic mutation/admission authority.
- Hash72 commits and chains admitted state transitions; a Hash72-shaped value does not independently define foundational validity.
- Hash216 preserves ordered identity, indexing, topology, archival evidence, and reusable continuation context after valid receipt closure.
- Canonical kernel arithmetic is exact; floating-point values may be bounded display, graphics, timing, benchmark, calibration, or foreign-format witnesses but do not silently replace exact authority.
- Ordered products such as `xy` and `yx` must not be collapsed unless the applicable exact law proves equivalence in the required domain.
- Every canonical mutation must be explicit, bounded, audited/admitted, receipt-bound, and replay-verifiable.
- Language-model output, GPU work, cache results, provider output, and remote-peer results are proposals/candidates/evidence until the inherited authority path admits them.

## Optimization law

HHS optimizes the amount of active work, not the definition of validity.

```text
DO NOT REMOVE INVARIANTS TO GET SPEED
REDUCE THE ACTIVE WORK REQUIRED TO DEMONSTRATE THE SAME INVARIANTS
```

This permits large global validity structure while keeping per-step work bounded through validated continuations, exact caches, vector indexing, dependency-scoped recomputation, selective hydration, compiled representations, branch ranking, and candidate parallelism.

```text
HOW FAST CAN WE FIND A VALID NEXT STATE?
```

is an optimization problem.

```text
WHAT COUNTS AS A VALID NEXT STATE?
```

is not a pass-level optimization variable.

Small local modules may participate in larger path-, time-, modality-, ordering-, correction-, or rollback-sensitive relations:

```text
LOCAL PURPOSE != GLOBAL SYSTEM ROLE
FILE ORGANIZATION != PROTECTION TOPOLOGY
LOCAL REDUNDANCY != GLOBAL REMOVABILITY
```

## Repository layout

The repository preserves a transitional hybrid of historical/root compatibility surfaces and structured package paths.

| Path | Responsibility |
|---|---|
| `hhs_runtime/` | Native/Python runtime substrate, kernel resolution, exact execution, C surfaces, continuation/replay, tests, and inherited/pre-pass-sensitive behavior |
| `hhs_python/` | Python runtime controller and ctypes bridge surfaces |
| `hhs_backend/` | FastAPI/service lifecycle, orchestration, assistant, routes, WebSockets, runtime services |
| `hhs_graph/` | Receipt, object, branch, and continuation topology |
| `hhs_storage/` | Durable state, receipt, Hash216/vector, replay, and persistence primitives |
| `native_projects/` | Pass-scoped native implementations, ABI bindings, contracts, evidence, deployment, and restart records |
| `hhs_gui/`, `applications/` | Human-operable runtime applications and development surfaces |
| `docs/` | Architecture, pass contracts, explanatory papers, deployment, and operational documentation |
| root runtime modules | Compatibility/historical entry points; path location alone does not prove a module is disposable or non-authoritative to inherited behavior |

Example compatibility path:

```text
hhs_general_runtime_layer_v1.py
→ hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1
```

Prefer current canonical package implementations for new code, while preserving and testing inherited behavior before moving or deleting historical surfaces.

## Pass 219 / 219B boundary

Current Pass 219 development is a cumulative C/C++ reusable membrane over inherited HHS behavior. It must expose rather than redefine the inherited authority chain.

Pass 219B selective phase/hydration work remains bounded and projection/candidate oriented where specified. PR #319 explicitly preserves zero canonical mutation, persistence, and Hash72 commit authority for the I7 optimization surface.

Do not treat an unmerged Pass 219/219B branch as authoritative `main` merely because its validation is green.

## Pass 220 boundary

The Pass 220 contract targets a professional native Linux HARMONICODE IDE/runtime/portable-VM development environment while preserving the same cumulative authority.

Its implementation gate remains:

```text
PASS 219 TERMINAL MERGE + EXACT-HEAD VERIFICATION
→ PASS 220 IMPLEMENTATION ADMISSION
```

PR #320 therefore remains preimplementation/non-promotional. Existing browser interfaces remain compatibility/remote/admin projections rather than the final primary local product direction.

## Downstream remote-agent and network targets

After terminal Pass 219 and Pass 220 closure, the first deployment target is an authenticated OpenAPI remote-agent object workspace. The effective remote model reuses the inherited operation registry, object/template authority, common action model, durable jobs, artifacts, receipts, and singleton VM81 path rather than creating a second object or mutation engine.

The later Universal Knowledge Economy contract extends that model into a peer/server network with immutable object lineage, Genesis/fork rules, reciprocal resource accounting, time-decaying credits, physical resource conservation, paid server contracts, subnet profiles, and PQC-secure federation.

These are downstream contracts, not current production-network claims.

## Inherited Pass 190 operation fabric

Pass 190 remains an important implemented historical/cumulative operation-fabric layer under:

```text
native_projects/hhs_pass190_operation_fabric/
```

Its validated durable-worker work established governed operation registration, dependency/schedule handling, worker claims, retry/recovery, receipts, generated SDK bindings, and API/visual projection under singleton authority.

Historical Pass 190 validation remains useful when that surface is impacted:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

Do not interpret this inherited operational section as meaning Pass 190 is still the current overall development frontier.

## Deployment operations

Repository-native deployment assets include historical DigitalOcean/systemd paths and later integrated-environment work. The existing operational runbook remains:

[`docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`](docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md)

It covers host preparation, service ordering, TLS routing, controlled upgrades/restarts, backups, restore/rollback, logs, isolation, troubleshooting, and maintenance for the applicable accepted deployment surfaces.

Historical deployment acceptance does not automatically satisfy Pass 220 native-VM, post-220 cloud/API, secure-database, downloadable-artifact, or UKE federation acceptance.

## Integrated visual environment

The inherited browser-based environment can still be launched through the historical compatibility path where dependencies are present:

```bash
python -m pip install -r requirements.txt
bash start.sh
```

Pass 220 explicitly moves the preferred future local interface toward a native Linux application/VM workspace. The web surface remains useful for compatibility, remote access, administration, and migration comparison.

## Harmonicode program and macro surfaces

The repository contains `.hhsprog` executable program surfaces, receipt-bearing run results, exact integer/rational operations, algebra-native macros, nested expansion, symbolic commitments, Hash72 receipt behavior, and replay verification.

Core compatibility/public files include:

```text
terminal_hhsprog_v5_macro_algebra.py
hhs_program_format_and_cli_v1.py
hhs_receipt_replay_verifier_v1.py
hhs_general_runtime_layer_v1.py
```

Identity-bearing lexical form, list/membrane structure, ordered operands, exact arithmetic, source/native bytes, and predecessor lineage must not be normalized away by later compilers or optimizers.

## Canonical documentation

Read these together:

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current ownership, authority, cumulative layering, low-latency law, and anti-drift rules
- [`docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md`](docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md) — pre-pass state-change/kernel-protection foundation
- [`docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md`](docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md) — single-authority/plug-in compatibility specification
- [`RUNTIME_FLOW.md`](RUNTIME_FLOW.md) — end-to-end transition, rollback, receipt, replay, cache, hydration, agent, API, and interface flow
- [`GLOSSARY.md`](GLOSSARY.md) — stable terminology
- [`AGENTS.md`](AGENTS.md) — repository navigation and implementation/refactor rules
- [`HHS_PASS_219_CPP_COMPOUND_SYMBOLIC_CONSTRAINT_RUNTIME_CONTRACT.md`](HHS_PASS_219_CPP_COMPOUND_SYMBOLIC_CONSTRAINT_RUNTIME_CONTRACT.md) — current numbered-pass runtime contract family
- [`HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md`](HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md) — downstream native development-environment contract
- [`docs/deployment/HHS_DEPLOYMENT_TARGET_1_OPENAPI_AGENT_OBJECT_WORKSPACE.md`](docs/deployment/HHS_DEPLOYMENT_TARGET_1_OPENAPI_AGENT_OBJECT_WORKSPACE.md) — first post-220 remote production target
- [`docs/deployment/HHS_UNIVERSAL_KNOWLEDGE_ECONOMY_NETWORK_CONTRACT.md`](docs/deployment/HHS_UNIVERSAL_KNOWLEDGE_ECONOMY_NETWORK_CONTRACT.md) — downstream peer/resource/federation architecture

## Baseline validation discipline

Use dependency-scoped validation rather than indiscriminately rerunning unaffected history.

For foundational/runtime changes, include the affected exact/no-float, ordered/noncommutative, cross-format, rollback, replay, VM81, Hash72/Hash216, ABI, and pass-specific tests.

Historical baseline commands remain available where relevant:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

A path, environment, performance, or deployment failure must be repaired forward at the affected boundary. Do not weaken foundational state validity, invariant checks, receipt continuity, ordered identity, or replay requirements to make a test pass.

## Disclosure boundary under consideration

The architecture allows a future release policy to expose public interoperability contracts while keeping selected pre-pass/kernel/algebra implementation details in validated compiled hydration-ROM or equivalent artifacts.

That policy is **not frozen by this README or the current documentation alignment**. In particular, no decision is made here about permanent non-upgradability, successor-ROM policy, or exact proprietary file boundaries.

System-wide documentation intentionally describes the invariant and authority model without publishing the exact pre-pass file-to-role map, private timing constants, or internal correction sequence.
