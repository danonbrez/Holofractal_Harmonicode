# Module Reachability Report — Pass 025

## Purpose

Pass 025 maintains the repository-wide runtime truth map. Every source-like module is classified by how it enters the HHS validated execution graph, or by why it is intentionally not executable.

## Status Counts

```json
{
  "API_REACHABLE": 12,
  "BOOT_REACHABLE": 14,
  "BUILD_REACHABLE": 2,
  "DEPRECATED": 1,
  "DOCUMENTED_ONLY": 1414,
  "GUI_REACHABLE": 3,
  "OWNED_ARTIFACT": 75,
  "PLUGIN_READY": 635,
  "SERVICE_REACHABLE": 331,
  "TOOL_REACHABLE": 1
}
```

## Canonical Surfaces

- Services discovered: **322**
- API routes discovered: **83**
- GUI runtime surfaces discovered: **2**
- Orphan records: **0**
- Plugin-ready candidates: **635**
- Pass 025 integration decisions: **1537**

## BOOT_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `hhs_runtime/HARMONICODE_VM_RUNTIME.c` | `hhs_runtime.HARMONICODE_VM_RUNTIME` | C runtime build target / ABI surface |
| `hhs_runtime/c/hhs_runtime_abi.c` | `hhs_runtime.c.hhs_runtime_abi` | C runtime build target / ABI surface |
| `hhs_runtime/c/hhs_runtime_abi.h` | `hhs_runtime.c.hhs_runtime_abi` | C runtime build target / ABI surface |
| `hhs_runtime/include/HARMONICODE_VM_RUNTIME.h` | `hhs_runtime.include.HARMONICODE_VM_RUNTIME` | C runtime build target / ABI surface |
| `hhs_runtime/include/hhs_hash216.h` | `hhs_runtime.include.hhs_hash216` | C runtime build target / ABI surface |
| `hhs_runtime/include/hhs_receipt.h` | `hhs_runtime.include.hhs_receipt` | C runtime build target / ABI surface |
| `hhs_runtime/include/hhs_tensor81.h` | `hhs_runtime.include.hhs_tensor81` | C runtime build target / ABI surface |
| `hhs_runtime/include/hhs_transport.h` | `hhs_runtime.include.hhs_transport` | C runtime build target / ABI surface |
| `hhs_runtime/main.py` | `hhs_runtime.main` | reachable from backend/runtime boot import graph |
| `hhs_runtime/runtime_event_bus.py` | `hhs_runtime.runtime_event_bus` | reachable from backend/runtime boot import graph |
| `hhs_runtime/runtime_event_schema.py` | `hhs_runtime.runtime_event_schema` | reachable from backend/runtime boot import graph |
| `hhs_runtime/runtime_kernel_bridge.py` | `hhs_runtime.runtime_kernel_bridge` | reachable from backend/runtime boot import graph |
| `hhs_runtime/runtime_ws.py` | `hhs_runtime.runtime_ws` | reachable from backend/runtime boot import graph |
| `hhs_runtime/src/hhs_hash216.c` | `hhs_runtime.src.hhs_hash216` | C runtime build target / ABI surface |


## SERVICE_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `harmonicode_modality_verbatim_ingestion_v1-1.py` | `harmonicode_modality_verbatim_ingestion_v1-1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `harmonicode_verbatim_semantic_database_v1.py` | `harmonicode_verbatim_semantic_database_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_backend/runtime/gui_projection_contract_v1.py` | `hhs_backend.runtime.gui_projection_contract_v1` | registered guarded service: live_gui_projection_contract.self_test |
| `hhs_backend/runtime/hhs_a_equals_b_phase_reintegration_v1.py` | `hhs_backend.runtime.hhs_a_equals_b_phase_reintegration_v1` | registered guarded service: branch_tree.a_equals_b_phase_reintegration_v1_self_test |
| `hhs_backend/runtime/hhs_agent_algorithm_identity_v1.py` | `hhs_backend.runtime.hhs_agent_algorithm_identity_v1` | registered guarded service: agent_economy.agent_algorithm_identity_v1_self_test |
| `hhs_backend/runtime/hhs_agent_behavioral_pressure_v1.py` | `hhs_backend.runtime.hhs_agent_behavioral_pressure_v1` | registered guarded service: agent_energy.agent_behavioral_pressure_v1_self_test |
| `hhs_backend/runtime/hhs_agent_contribution_provenance_v1.py` | `hhs_backend.runtime.hhs_agent_contribution_provenance_v1` | registered guarded service: agent_economy.agent_contribution_provenance_v1_self_test |
| `hhs_backend/runtime/hhs_agent_economy_orchestrator_v1.py` | `hhs_backend.runtime.hhs_agent_economy_orchestrator_v1` | registered guarded service: agent_economy.agent_economy_orchestrator_v1_self_test |
| `hhs_backend/runtime/hhs_agent_energy_epoch_v1.py` | `hhs_backend.runtime.hhs_agent_energy_epoch_v1` | registered guarded service: agent_energy.agent_energy_epoch_v1_self_test |
| `hhs_backend/runtime/hhs_agent_energy_transaction_receipt_v1.py` | `hhs_backend.runtime.hhs_agent_energy_transaction_receipt_v1` | registered guarded service: agent_energy.agent_energy_transaction_receipt_v1_self_test |
| `hhs_backend/runtime/hhs_agent_experience_commitment_v1.py` | `hhs_backend.runtime.hhs_agent_experience_commitment_v1` | registered guarded service: agent_economy.agent_experience_commitment_v1_self_test |
| `hhs_backend/runtime/hhs_agent_fitness_vector_v1.py` | `hhs_backend.runtime.hhs_agent_fitness_vector_v1` | registered guarded service: agent_economy.agent_fitness_vector_v1_self_test |
| `hhs_backend/runtime/hhs_agent_mutation_lineage_v1.py` | `hhs_backend.runtime.hhs_agent_mutation_lineage_v1` | registered guarded service: agent_economy.agent_mutation_lineage_v1_self_test |
| `hhs_backend/runtime/hhs_agent_tensor_revalidation_v1.py` | `hhs_backend.runtime.hhs_agent_tensor_revalidation_v1` | registered guarded service: agent_tensor.agent_tensor_revalidation_v1_self_test |
| `hhs_backend/runtime/hhs_agent_tensor_weight_update_v1.py` | `hhs_backend.runtime.hhs_agent_tensor_weight_update_v1` | registered guarded service: agent_tensor.agent_tensor_weight_update_v1_self_test |
| `hhs_backend/runtime/hhs_alignment_agent_v1.py` | `hhs_backend.runtime.hhs_alignment_agent_v1` | registered guarded service: alignment.alignment_agent_v1_self_test |
| `hhs_backend/runtime/hhs_alignment_drift_detector_v1.py` | `hhs_backend.runtime.hhs_alignment_drift_detector_v1` | registered guarded service: alignment.alignment_drift_detector_v1_self_test |
| `hhs_backend/runtime/hhs_alignment_execution_receipt_v1.py` | `hhs_backend.runtime.hhs_alignment_execution_receipt_v1` | registered guarded service: alignment.alignment_execution_receipt_v1_self_test |
| `hhs_backend/runtime/hhs_artifact_lineage_registry_v1.py` | `hhs_backend.runtime.hhs_artifact_lineage_registry_v1` | registered guarded service: artifact_lineage_registry.self_test |
| `hhs_backend/runtime/hhs_attention_authority_separation_v1.py` | `hhs_backend.runtime.hhs_attention_authority_separation_v1` | registered guarded service: authority.attention_authority_separation_self_test |
| `hhs_backend/runtime/hhs_authority_enforced_dispatch_v1.py` | `hhs_backend.runtime.hhs_authority_enforced_dispatch_v1` | registered guarded service: authority_activation.authority_enforced_dispatch_self_test |
| `hhs_backend/runtime/hhs_authority_enforced_execution_receipt_v1.py` | `hhs_backend.runtime.hhs_authority_enforced_execution_receipt_v1` | registered guarded service: authority_activation.execution_receipt_self_test |
| `hhs_backend/runtime/hhs_authority_enforced_runtime_dispatch_v1.py` | `hhs_backend.runtime.hhs_authority_enforced_runtime_dispatch_v1` | registered guarded service: authority_activation.runtime_dispatch_surface_self_test |
| `hhs_backend/runtime/hhs_binary_compatibility_execution_receipt_v1.py` | `hhs_backend.runtime.hhs_binary_compatibility_execution_receipt_v1` | registered guarded service: binary_trinary.binary_compatibility_execution_receipt_v1_self_test |
| `hhs_backend/runtime/hhs_binary_operator_translation_v1.py` | `hhs_backend.runtime.hhs_binary_operator_translation_v1` | registered guarded service: binary_trinary.binary_operator_translation_v1_self_test |
| `hhs_backend/runtime/hhs_binary_pair_state_v1.py` | `hhs_backend.runtime.hhs_binary_pair_state_v1` | registered guarded service: binary_trinary.binary_pair_state_v1_self_test |
| `hhs_backend/runtime/hhs_binary_to_trinary_translator_v1.py` | `hhs_backend.runtime.hhs_binary_to_trinary_translator_v1` | registered guarded service: binary_trinary.binary_to_trinary_translator_v1_self_test |
| `hhs_backend/runtime/hhs_binary_trinary_round_trip_validator_v1.py` | `hhs_backend.runtime.hhs_binary_trinary_round_trip_validator_v1` | registered guarded service: binary_trinary.binary_trinary_round_trip_validator_v1_self_test |
| `hhs_backend/runtime/hhs_binary_word_trinary_packet_v1.py` | `hhs_backend.runtime.hhs_binary_word_trinary_packet_v1` | registered guarded service: binary_trinary.binary_word_trinary_packet_v1_self_test |
| `hhs_backend/runtime/hhs_bounded_partial_reconstruction_v1.py` | `hhs_backend.runtime.hhs_bounded_partial_reconstruction_v1` | registered guarded service: total_system.bounded_partial_reconstruction_v1_self_test |
| `hhs_backend/runtime/hhs_bounded_rejection_authority_v1.py` | `hhs_backend.runtime.hhs_bounded_rejection_authority_v1` | registered guarded service: authority_rejection.bounded_rejection_authority_v1_self_test |
| `hhs_backend/runtime/hhs_branch_authority_expiration_v1.py` | `hhs_backend.runtime.hhs_branch_authority_expiration_v1` | registered guarded service: branch_tree.branch_authority_expiration_v1_self_test |
| `hhs_backend/runtime/hhs_branch_contradiction_localizer_v1.py` | `hhs_backend.runtime.hhs_branch_contradiction_localizer_v1` | registered guarded service: branch_tree.branch_contradiction_localizer_v1_self_test |
| `hhs_backend/runtime/hhs_branch_execution_receipt_v1.py` | `hhs_backend.runtime.hhs_branch_execution_receipt_v1` | registered guarded service: branch_tree.branch_execution_receipt_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_authority_graph_v1.py` | `hhs_backend.runtime.hhs_canonical_authority_graph_v1` | registered guarded service: authority.authority_graph_self_test |
| `hhs_backend/runtime/hhs_canonical_federated_merge_candidate_v1.py` | `hhs_backend.runtime.hhs_canonical_federated_merge_candidate_v1` | registered guarded service: authority_reconciliation.canonical_federated_merge_candidate_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_federated_merge_decision_v1.py` | `hhs_backend.runtime.hhs_canonical_federated_merge_decision_v1` | registered guarded service: authority_reconciliation.canonical_federated_merge_decision_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_federated_state_reconciliation_v1.py` | `hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1` | registered guarded service: authority_reconciliation.canonical_federated_state_reconciliation_self_test |
| `hhs_backend/runtime/hhs_canonical_federated_transaction_commit_v1.py` | `hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1` | registered guarded service: authority_transaction.canonical_federated_transaction_commit_self_test |
| `hhs_backend/runtime/hhs_canonical_federated_transaction_decision_v1.py` | `hhs_backend.runtime.hhs_canonical_federated_transaction_decision_v1` | registered guarded service: authority_transaction.canonical_federated_transaction_decision_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_formal_manifold_state_v1.py` | `hhs_backend.runtime.hhs_canonical_formal_manifold_state_v1` | registered guarded service: manifold_execution.canonical_formal_manifold_state_self_test |
| `hhs_backend/runtime/hhs_canonical_prompt_state_v1.py` | `hhs_backend.runtime.hhs_canonical_prompt_state_v1` | registered guarded service: alignment.canonical_prompt_state_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_resolution_agent_identity_v1.py` | `hhs_backend.runtime.hhs_canonical_resolution_agent_identity_v1` | registered guarded service: agent_economy.canonical_resolution_agent_identity_v1_self_test |
| `hhs_backend/runtime/hhs_canonical_response_state_v1.py` | `hhs_backend.runtime.hhs_canonical_response_state_v1` | registered guarded service: alignment.canonical_response_state_v1_self_test |
| `hhs_backend/runtime/hhs_capability_contract_v1.py` | `hhs_backend.runtime.hhs_capability_contract_v1` | registered guarded service: capability_contract.self_test |
| `hhs_backend/runtime/hhs_capability_fallback_plan_v1.py` | `hhs_backend.runtime.hhs_capability_fallback_plan_v1` | registered guarded service: capability_fallback_plan.self_test |
| `hhs_backend/runtime/hhs_capability_lease_issuer_v1.py` | `hhs_backend.runtime.hhs_capability_lease_issuer_v1` | registered guarded service: authority_activation.capability_lease_issuer_self_test |
| `hhs_backend/runtime/hhs_capability_lease_registry_v1.py` | `hhs_backend.runtime.hhs_capability_lease_registry_v1` | registered guarded service: authority_activation.capability_lease_registry_self_test |
| `hhs_backend/runtime/hhs_capability_lease_revocation_v1.py` | `hhs_backend.runtime.hhs_capability_lease_revocation_v1` | registered guarded service: authority_activation.capability_lease_revocation_self_test |
| `hhs_backend/runtime/hhs_capability_policy_gate_v1.py` | `hhs_backend.runtime.hhs_capability_policy_gate_v1` | registered guarded service: capability_policy_gate.self_test |
| `hhs_backend/runtime/hhs_capability_provider_registry_v1.py` | `hhs_backend.runtime.hhs_capability_provider_registry_v1` | registered guarded service: capability_provider_registry.self_test |
| `hhs_backend/runtime/hhs_capability_resolution_v1.py` | `hhs_backend.runtime.hhs_capability_resolution_v1` | registered guarded service: capability_resolution.self_test |
| `hhs_backend/runtime/hhs_closed_branch_contract_v1.py` | `hhs_backend.runtime.hhs_closed_branch_contract_v1` | registered guarded service: branch_tree.closed_branch_contract_v1_self_test |
| `hhs_backend/runtime/hhs_closed_loop_three_lane_program_weaving_v1.py` | `hhs_backend.runtime.hhs_closed_loop_three_lane_program_weaving_v1` | registered guarded service: program_weaving.closed_loop_three_lane_program_weaving_v1_self_test |
| `hhs_backend/runtime/hhs_closure_dimension_receipt_v1.py` | `hhs_backend.runtime.hhs_closure_dimension_receipt_v1` | registered guarded service: total_system.closure_dimension_receipt_v1_self_test |
| `hhs_backend/runtime/hhs_compiler_ir_v1.py` | `hhs_backend.runtime.hhs_compiler_ir_v1` | registered guarded service: compiler_ir.self_test |
| `hhs_backend/runtime/hhs_component_competency_registry_v1.py` | `hhs_backend.runtime.hhs_component_competency_registry_v1` | registered guarded service: authority.competency_registry_self_test |
| `hhs_backend/runtime/hhs_conflict_preserving_merge_policy_v1.py` | `hhs_backend.runtime.hhs_conflict_preserving_merge_policy_v1` | registered guarded service: authority_reconciliation.conflict_preserving_merge_policy_v1_self_test |
| `hhs_backend/runtime/hhs_constraint_difficulty_profile_v1.py` | `hhs_backend.runtime.hhs_constraint_difficulty_profile_v1` | registered guarded service: agent_economy.constraint_difficulty_profile_v1_self_test |
| `hhs_backend/runtime/hhs_context_continuity_journal_v1.py` | `hhs_backend.runtime.hhs_context_continuity_journal_v1` | registered guarded service: phase_folding.context_continuity_journal_v1_self_test |
| … | … | 271 additional records omitted from this summary; see JSON manifest. |


## API_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `hhs_backend/api/runtime_routes.py` | `hhs_backend.api.runtime_routes` | reachable through canonical backend/API route graph |
| `hhs_backend/runtime/runtime_event_schema.py` | `hhs_backend.runtime.runtime_event_schema` | reachable through canonical backend/API route graph |
| `hhs_backend/runtime/runtime_ws.py` | `hhs_backend.runtime.runtime_ws` | reachable through canonical backend/API route graph |
| `hhs_backend/server.py` | `hhs_backend.server` | reachable through canonical backend/API route graph |
| `hhs_graph/hhs_multimodal_receipt_graph_v1.py` | `hhs_graph.hhs_multimodal_receipt_graph_v1` | reachable through canonical backend/API route graph |
| `hhs_python/runtime/hhs_runtime_controller.py` | `hhs_python.runtime.hhs_runtime_controller` | reachable through canonical backend/API route graph |
| `hhs_python/runtime/hhs_runtime_emulator.py` | `hhs_python.runtime.hhs_runtime_emulator` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_filesystem_hash72_ledger_v1.py` | `hhs_runtime.hhs_filesystem_hash72_ledger_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_loshu_phase_embedding_v1.py` | `hhs_runtime.hhs_loshu_phase_embedding_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_receipt_vector_index_v1.py` | `hhs_runtime.hhs_receipt_vector_index_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_repo_paths_v1.py` | `hhs_runtime.hhs_repo_paths_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_service_registry_v1.py` | `hhs_runtime.hhs_service_registry_v1` | reachable through canonical backend/API route graph |


## GUI_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `hhs_gui/main.tsx` | `hhs_gui.main` | frontend runtime/contract surface |
| `hhs_gui/src/App.tsx` | `hhs_gui.src.App` | frontend runtime/contract surface |
| `native_projects/hhs_ide_workspace/workspace_ui/app.js` | `native_projects.hhs_ide_workspace.workspace_ui.app` | Pass 105.3 native ownership: native_projects.hhs_ide_workspace.hhs_native_workspace_project_v1 via tests/test_hhs_pass074_unified_ide_workspace_v1.py |


## PLUGIN_READY Candidates

These are not failures. They are likely integration candidates that have service/engine/adapter/validator shape but are not currently part of the canonical dispatch graph.

| Path | Module | Reason |
|---|---|---|
| `HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py` | `HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `examples/hhs_loshu_phase_embedding_demo_v1.py` | `examples.hhs_loshu_phase_embedding_demo_v1` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/App.tsx` | `gui.hhs-mobile-runtime-console.src.App` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/api/hhsApi.ts` | `gui.hhs-mobile-runtime-console.src.api.hhsApi` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/audioPhaseClient.ts` | `gui.hhs-mobile-runtime-console.src.audioPhaseClient` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/calculatorExpressionModel.ts` | `gui.hhs-mobile-runtime-console.src.calculatorExpressionModel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/AlertPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.AlertPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/AssistantWorkspace.tsx` | `gui.hhs-mobile-runtime-console.src.components.AssistantWorkspace` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.CalculatorPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanelV2.tsx` | `gui.hhs-mobile-runtime-console.src.components.CalculatorPanelV2` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/CertificationPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.CertificationPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/ExecutionPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.ExecutionPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/IntentBar.tsx` | `gui.hhs-mobile-runtime-console.src.components.IntentBar` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/LedgerPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.LedgerPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/OperatorPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.OperatorPanel` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/PhaseRing3D.tsx` | `gui.hhs-mobile-runtime-console.src.components.PhaseRing3D` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/ReceiptStream.tsx` | `gui.hhs-mobile-runtime-console.src.components.ReceiptStream` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/RuntimeTelemetry.tsx` | `gui.hhs-mobile-runtime-console.src.components.RuntimeTelemetry` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/components/StatusHeader.tsx` | `gui.hhs-mobile-runtime-console.src.components.StatusHeader` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/displayPhaseAnalysis.ts` | `gui.hhs-mobile-runtime-console.src.displayPhaseAnalysis` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/hooks/useHHSStream.ts` | `gui.hhs-mobile-runtime-console.src.hooks.useHHSStream` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/hooks/useRuntime.ts` | `gui.hhs-mobile-runtime-console.src.hooks.useRuntime` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/main.tsx` | `gui.hhs-mobile-runtime-console.src.main` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/runtimeData.ts` | `gui.hhs-mobile-runtime-console.src.runtimeData` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `gui/hhs-mobile-runtime-console/src/useCalculatorDoc.ts` | `gui.hhs-mobile-runtime-console.src.useCalculatorDoc` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `harmonicode_agent_v43_3_dna_lockcore_patched_selfsolving_hash72authority_locked-7.py` | `harmonicode_agent_v43_3_dna_lockcore_patched_selfsolving_hash72authority_locked-7` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_backend/runtime/distributed_consensus_runtime.py` | `hhs_backend.runtime.distributed_consensus_runtime` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/distributed_runtime_node_v1.py` | `hhs_backend.runtime.distributed_runtime_node_v1` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/hhs_total_system_recursive_holographic_closure_v1.py` | `hhs_backend.runtime.hhs_total_system_recursive_holographic_closure_v1` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_adaptive_goal_engine.py` | `hhs_backend.runtime.runtime_adaptive_goal_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_agentic_cognition_layer.py` | `hhs_backend.runtime.runtime_agentic_cognition_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_autonomous_research_layer.py` | `hhs_backend.runtime.runtime_autonomous_research_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_event_bus.py` | `hhs_backend.runtime.runtime_event_bus` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_graph_projection.py` | `hhs_backend.runtime.runtime_graph_projection` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_backend/runtime/runtime_multimodal_embedding_router.py` | `hhs_backend.runtime.runtime_multimodal_embedding_router` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_multinode_goal_consensus.py` | `hhs_backend.runtime.runtime_multinode_goal_consensus` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_orchestrator.py` | `hhs_backend.runtime.runtime_orchestrator` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_prediction_engine.py` | `hhs_backend.runtime.runtime_prediction_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_receipt_chain.py` | `hhs_backend.runtime.runtime_receipt_chain` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_recursive_toolchain_layer.py` | `hhs_backend.runtime.runtime_recursive_toolchain_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_rehydration_engine.py` | `hhs_backend.runtime.runtime_rehydration_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_replay_engine.py` | `hhs_backend.runtime.runtime_replay_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_replay_topology.py` | `hhs_backend.runtime.runtime_replay_topology` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_self_modification_governor.py` | `hhs_backend.runtime.runtime_self_modification_governor` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_semantic_memory_engine.py` | `hhs_backend.runtime.runtime_semantic_memory_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_server.py` | `hhs_backend.runtime.runtime_server` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_backend/runtime/runtime_snapshot_codec.py` | `hhs_backend.runtime.runtime_snapshot_codec` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_transport_protocol.py` | `hhs_backend.runtime.runtime_transport_protocol` | source has integration shape but no current guarded route/service |
| `hhs_backend/websocket/runtime_stream_manager.py` | `hhs_backend.websocket.runtime_stream_manager` | source has integration shape but no current guarded route/service |
| `hhs_backend_final_certification_v1.py` | `hhs_backend_final_certification_v1` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_control_flow_gates_v1.py` | `hhs_control_flow_gates_v1` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_execution_geometry_v1.py` | `hhs_execution_geometry_v1` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_foundation/HHS-M001.py` | `hhs_foundation.HHS-M001` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M002.py` | `hhs_foundation.HHS-M002` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M003.py` | `hhs_foundation.HHS-M003` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M004.py` | `hhs_foundation.HHS-M004` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M005.py` | `hhs_foundation.HHS-M005` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M006.py` | `hhs_foundation.HHS-M006` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS-M007.py` | `hhs_foundation.HHS-M007` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M001.py` | `hhs_foundation.HHS_M001` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M002.py` | `hhs_foundation.HHS_M002` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M003.py` | `hhs_foundation.HHS_M003` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M004.py` | `hhs_foundation.HHS_M004` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M005.py` | `hhs_foundation.HHS_M005` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M006.py` | `hhs_foundation.HHS_M006` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/HHS_M007.py` | `hhs_foundation.HHS_M007` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/__init__.py` | `hhs_foundation` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/constitutional_validator.py` | `hhs_foundation.constitutional_validator` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_foundation/meaning_conservation.py` | `hhs_foundation.meaning_conservation` | Pass 025 integration decision: constitutional compatibility shim; callable only through canonical foundational standards module |
| `hhs_general_runtime_layer_v1.py` | `hhs_general_runtime_layer_v1` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
| `hhs_gui/postcss.config.js` | `hhs_gui.postcss.config` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime/runtime_workspace_objects.py` | `hhs_gui.runtime.runtime_workspace_objects` | source has integration shape but no current guarded route/service |
| `hhs_gui/runtime_apps/breadboard/HHSRuntimeBreadboard.tsx` | `hhs_gui.runtime_apps.breadboard.HHSRuntimeBreadboard` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/breadboard/HHSRuntimeTransportOverlay.tsx` | `hhs_gui.runtime_apps.breadboard.HHSRuntimeTransportOverlay` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/breadboard/RuntimeBreadboard.tsx` | `hhs_gui.runtime_apps.breadboard.RuntimeBreadboard` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/calculator/HHSCalculatorGraphProjection.tsx` | `hhs_gui.runtime_apps.calculator.HHSCalculatorGraphProjection` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/calculator/HHSCalculatorSurface.tsx` | `hhs_gui.runtime_apps.calculator.HHSCalculatorSurface` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/calculator/RuntimeCalculator.tsx` | `hhs_gui.runtime_apps.calculator.RuntimeCalculator` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/instruments/ReceiptInspector.tsx` | `hhs_gui.runtime_apps.instruments.ReceiptInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_apps/instruments/ReplayTimeline.tsx` | `hhs_gui.runtime_apps.instruments.ReplayTimeline` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/artifacts/ArtifactLineageViewer.tsx` | `hhs_gui.runtime_os.artifacts.ArtifactLineageViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/artifacts/ArtifactPipelinePanel.tsx` | `hhs_gui.runtime_os.artifacts.ArtifactPipelinePanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/AttentionAuthoritySeparationViewer.tsx` | `hhs_gui.runtime_os.authority.AttentionAuthoritySeparationViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/AuthorityActivationInspector.tsx` | `hhs_gui.runtime_os.authority.AuthorityActivationInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/AuthorityDispatchViewer.tsx` | `hhs_gui.runtime_os.authority.AuthorityDispatchViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/BoundedRejectionAuthorityPanel.tsx` | `hhs_gui.runtime_os.authority.BoundedRejectionAuthorityPanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CanonicalAuthorityGraphPanel.tsx` | `hhs_gui.runtime_os.authority.CanonicalAuthorityGraphPanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CanonicalContinuationInspector.tsx` | `hhs_gui.runtime_os.authority.CanonicalContinuationInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CanonicalStateReconciliationPanel.tsx` | `hhs_gui.runtime_os.authority.CanonicalStateReconciliationPanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CapabilityLeaseMatrix.tsx` | `hhs_gui.runtime_os.authority.CapabilityLeaseMatrix` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CapabilityLeasePanel.tsx` | `hhs_gui.runtime_os.authority.CapabilityLeasePanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CommonAncestorViewer.tsx` | `hhs_gui.runtime_os.authority.CommonAncestorViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CompetencyAuthorityMatrix.tsx` | `hhs_gui.runtime_os.authority.CompetencyAuthorityMatrix` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/ConflictPreservingMergePanel.tsx` | `hhs_gui.runtime_os.authority.ConflictPreservingMergePanel` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/CrossRoleHandoffViewer.tsx` | `hhs_gui.runtime_os.authority.CrossRoleHandoffViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/DerivationEquivalenceInspector.tsx` | `hhs_gui.runtime_os.authority.DerivationEquivalenceInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/ExecutionCheckpointViewer.tsx` | `hhs_gui.runtime_os.authority.ExecutionCheckpointViewer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/ExecutionReceiptInspector.tsx` | `hhs_gui.runtime_os.authority.ExecutionReceiptInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/FederatedConflictSetInspector.tsx` | `hhs_gui.runtime_os.authority.FederatedConflictSetInspector` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/authority/FederatedMergeCandidateViewer.tsx` | `hhs_gui.runtime_os.authority.FederatedMergeCandidateViewer` | frontend source not yet explicitly mapped to runtime bridge |
| … | … | 535 additional records omitted from this summary; see JSON manifest. |


## ORPHAN Candidates

These require explicit integration, deprecation, or documentation-only classification in subsequent passes.

| Path | Module | Reason |
|---|---|---|
| — | — | — |


## Kernel Witness

The manifest itself is sealed with a C `u^72` Digital DNA Hash72 kernel witness.

```json
{
  "canonical_payload": "\"{\\\"api_route_count\\\": 83, \\\"orphan_count\\\": 0, \\\"record_count\\\": 2488, \\\"schema\\\": \\\"HHS_RUNTIME_REACHABILITY_MANIFEST_V1\\\", \\\"service_count\\\": 322, \\\"status_counts\\\": {\\\"API_REACHABLE\\\": 12, \\\"BOOT_REACHABLE\\\": 14, \\\"BUILD_REACHABLE\\\": 2, \\\"DEPRECATED\\\": 1, \\\"DOCUMENTED_ONLY\\\": 1414, \\\"GUI_REACHABLE\\\": 3, \\\"OWNED_ARTIFACT\\\": 75, \\\"PLUGIN_READY\\\": 635, \\\"SERVICE_REACHABLE\\\": 331, \\\"TOOL_REACHABLE\\\": 1}, \\\"version\\\": \\\"PASS_032\\\"}\"",
  "digest": "gA<j1(wO!Y7ojITzy0A9STHMntWxCe2teP8J638U1lVaPhjtYPCI0iG(*/3bx?3et!h!2G/)",
  "dna": "gA<j1(wO!Y7ojITzy0A9STHMntWxCe2teP8J638U1lVaPhjtYPCI0iG(*/3bx?3et!h!2G/)",
  "label": "hhs_runtime_reachability_manifest_v1",
  "positions": [
    16,
    36,
    68,
    19,
    1,
    66,
    32,
    50,
    70,
    60,
    7,
    24,
    19,
    44,
    55,
    35,
    34,
    0,
    36,
    9,
    54,
    55,
    43,
    48,
    23,
    29,
    58,
    33,
    38,
    14,
    2,
    29,
    14,
    51,
    8,
    45,
    6,
    3,
    8,
    56,
    1,
    21,
    57,
    10,
    51,
    17,
    19,
    29,
    60,
    51,
    38,
    44,
    0,
    18,
    42,
    66,
    64,
    65,
    3,
    11,
    33,
    71,
    3,
    14,
    29,
    70,
    17,
    70,
    2,
    42,
    65,
    67
  ],
  "rotation_profile": [
    16,
    -37,
    -6,
    -56,
    69,
    -11,
    -46,
    43,
    -10,
    51,
    -3,
    -59,
    79,
    -41,
    -31,
    -52,
    90,
    -17,
    -54,
    62,
    34,
    -38,
    21,
    25,
    -73,
    76,
    -40,
    78,
    -62,
    57,
    -100,
    -74,
    54,
    -54,
    46,
    -62,
    42,
    38,
    42,
    -55,
    -39,
    -20,
    15,
    39,
    -65,
    44,
    45,
    -18,
    -60,
    2,
    -12,
    65,
    -52,
    -35,
    -12,
    83,
    -64,
    8,
    17,
    24,
    -27,
    10,
    85,
    -121,
    37,
    -67,
    95,
    3,
    6,
    -27,
    -5,
    104
  ],
  "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
  "trace_count": 474,
  "zero_sum": true
}
```
