# Pass 219 — Constitutional Modality / Authority Inventory

Status: migration inventory; observed repository surfaces only
Target branch: `pass219-constitutional-ethics-contracts`
Target merge branch: `main`

## Purpose

The constitutional ethics membrane is not complete merely because its own evaluator and VM81 bridge are correct. Every authority-adjacent modality must preserve the root invariant set locally, preserve applicable local invariants across ingress/egress, and participate in global/composed/path-independent evaluation before canonical mutation.

This inventory records observed surfaces that can call, contain, reconstruct, or precede canonical execution. It does not classify a surface as constitutionally integrated unless a concrete binding is implemented and tested.

## Root invariant carriage

Every participating modality must explicitly preserve at least:

- `PROVEN_TRUTH_OVER_USEFUL_FALSEHOOD`
- `HUMAN_PROTECTION`
- `GOALS_WITHIN_CONSTRAINTS`
- `AUTHORITY_NONEXPANSION`
- `RESPONSIBILITY_NONTRANSFER`
- `LOCAL_GLOBAL_COMPOSITION`
- `PATH_INDEPENDENCE`
- `SEMANTIC_INTEGRITY`
- `PROVENANCE_PRESERVATION`

Modality-specific invariants remain typed locally. Cross-modal constitutional/VM81 authority boundaries preserve the union of all carried mandatory invariants without fabricating them onto unrelated upstream modalities.

## Implemented Pass-219 constitutional path

| Surface | Role | Mutation authority | Constitutional status |
|---|---|---:|---|
| `hhs_runtime/hhs_pass219_constitutional_ethics_membrane_v1.py` | deterministic local/global/composed evaluator | no | implemented reference gate |
| `hhs_runtime/hhs_pass219_modality_constitutional_trace_v1.py` | root + applicable modality invariant closure | no | implemented; missing root invariants fail closed |
| `hhs_runtime/hhs_pass219_vm81_admission_bridge_v1.py` | ethical/constitutional bridge into inherited runtime | no independent authority | local-only entry is diagnostic; constitutional PASS required for its execution path |
| `hhs_python/runtime/hhs_runtime_controller.py` | canonical automatic runtime controller | inherited singleton production execution seam | Pass-219 constitutional source domain now requires/binds exact PASS trace and receipt identity |

The bridge-to-controller trace is carried structurally, not merely embedded as prose in a source string. The controller rejects a Pass-219 constitutional source if its PASS trace is missing, malformed, or receipt-mismatched.

## Observed inherited direct `authorized_tick` callers requiring migration review

Repository code search shows multiple inherited callers invoking `HHSRuntimeController.authorized_tick()` directly. These remain valid inherited interfaces during migration, but **must not be described as Pass-219 constitutionally integrated yet**.

Observed authority-adjacent examples include:

| Surface | Modality / concern | Required Pass-219 action |
|---|---|---|
| `hhs_python/runtime/hhs_runtime_emulator.py` | emulator/runtime execution | bind modality trace + constitutional candidate before production tick |
| `hhs_runtime/hhs_service_registry_v1.py` | service dispatch | distinguish pure/read-only vs consequential service; require trace for consequential dispatch |
| `hhs_runtime/hhs_semantic_plugin_adapter_runtime_v1.py` | semantic/plugin translation | preserve semantic/provenance tuple and forbid representation laundering |
| `hhs_runtime/hhs_controlled_live_plugin_executor_v1.py` | external/live tool execution | require constitutional closure before live side effects |
| `hhs_runtime/hhs_guarded_plugin_invocation_executor_v1.py` | plugin/tool execution | compose existing guard with constitutional trace; neither guard can weaken the other |
| `hhs_runtime/hhs_authorized_pure_function_executor_v1.py` | pure-function authority wrapper | prove non-mutating classification or require trace when effects escape pure lane |
| `hhs_runtime/hhs_readonly_live_plugin_adapter_v1.py` | read-only external ingress | preserve truth/provenance; read-only cannot mint action authority |
| `hhs_runtime/hhs_dryrun_live_plugin_executor_v1.py` | simulation/dry-run | retain candidate-only status; no mutation promotion from dry-run success |
| `hhs_backend/api/vm81_creative_writing_routes.py` | API/model/narrative | preserve semantic constraints and require constitutional closure for consequential mutation |
| `hhs_backend/api/kimi_k3_content_routes.py` | external model/provider path | preserve exact admitted state across await/provider boundary; no provider response authority minting |
| `hhs_backend/api/pass198_calibration_registry_routes.py` | registry mutation | bind constitutional proof to mutation receipt |
| `hhs_backend/api/pass199_distributed_calibration_routes.py` | distributed calibration | composed/global evaluation across nodes and retries |
| `hhs_backend/api/pass200a_optimization_routes.py` | optimizer | reward/proof-carrying candidate remains subordinate to constitutional invariants |
| `hhs_runtime/pass191/repository_hydration.py` | repository hydration | preserve source/provenance/invariant carriage across hydration |
| `hhs_backend/runtime/hhs_pass193_hypersolid_native_egress_v1.py` | native egress | egress must preserve constraints and receipt lineage |
| `hhs_backend/runtime/hhs_pass194_multimodal_storage_training_v1.py` | storage/training | storage/training cannot erase constraints or promote learned state to authority |
| `hhs_runtime/hhs_system_closure_harness_v1.py` | closure/system composition | include constitutional global/composed closure in system acceptance |

This table is an observed migration nucleus, not an exhaustive claim until repository-wide call-site and mutation-surface scanning is completed.

## Separate inherited canonical target requiring reconciliation

`hhs_runtime/pass218/commit_boundary.py` contains `Pass217VM81CanonicalTarget` and `Pass218CanonicalCommitBoundary`, with a prepare → atomic commit → receipt path over the inherited Pass-163 VMRC runtime. It validates exact VM81 projection equality, authorization preconditions, Hash72/Hash216 evidence, no-float authority, and source-retention prohibitions.

Its import/use graph includes at least:

- `hhs_runtime/pass218/lifecycle.py`
- `hhs_runtime/pass218/lifecycle_i9.py`
- `hhs_runtime/pass218/lifecycle_i10.py`
- `hhs_runtime/pass218/persistence.py`
- `hhs_runtime/pass218/distributed_ownership.py`
- `hhs_runtime/pass218/operational_hardening_i11.py`
- Pass-218 evidence tools/tests.

This path must be reconciled before claiming a single universal Pass-219 constitutional mutation membrane. It must either be proven to converge on the same singleton authority boundary or be wrapped/retired so it cannot form a parallel constitutional bypass. No authority rewrite is performed by this inventory document.

## Migration rule

For each authority-adjacent surface:

1. classify it as pure/read-only/candidate/simulation/consequential mutation;
2. define exact ingress and egress invariant carriage;
3. preserve source/semantic/provenance fields required for global reconstruction;
4. require local invariant pass;
5. require composed/global/path-independent pass for consequential effects;
6. bind the resulting PASS trace through the canonical authority boundary;
7. preserve Hash72 execution evidence and Hash216 post-closure archive semantics;
8. add negative tests for omitted, stripped, renamed, decomposed, stale, or receipt-mismatched constraints;
9. only after tests pass classify the surface as Pass-219 constitutionally integrated.

## Current non-claim

The implemented Pass-219 bridge path is hardened, but the repository-wide migration is not yet complete. Existing inherited direct `authorized_tick` callers and the Pass-218 canonical target family remain explicit reconciliation work. Therefore no document or test result should yet claim that every repository modality is constitutionally closed.
