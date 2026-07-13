# Module Reachability Report — Pass 025

## Purpose

Pass 025 maintains the repository-wide runtime truth map. Every source-like module is classified by how it enters the HHS validated execution graph, or by why it is intentionally not executable.

## Status Counts

```json
{
  "API_REACHABLE": 9,
  "BOOT_REACHABLE": 14,
  "DOCUMENTED_ONLY": 275,
  "GUI_REACHABLE": 2,
  "PLUGIN_READY": 348,
  "SERVICE_REACHABLE": 29
}
```

## Canonical Surfaces

- Services discovered: **19**
- API routes discovered: **18**
- GUI runtime surfaces discovered: **2**
- Orphan records: **0**
- Plugin-ready candidates: **348**
- Pass 025 integration decisions: **578**

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
| `hhs_database_integration_layer_v1.py` | `hhs_database_integration_layer_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_foundation/hhs_foundational_standards_v1.py` | `hhs_foundation.hhs_foundational_standards_v1` | registered guarded service: foundational_standards.self_test |
| `hhs_python/runtime/hhs_ctypes_bridge.py` | `hhs_python.runtime.hhs_ctypes_bridge` | registered guarded service: c_bridge.abi_self_test |
| `hhs_runtime/hhs_authority_gate_v1.py` | `hhs_runtime.hhs_authority_gate_v1` | registered guarded service: authority_gate.self_test |
| `hhs_runtime/hhs_guarded_plugin_adapters_v1.py` | `hhs_runtime.hhs_guarded_plugin_adapters_v1` | registered guarded service: guarded_plugin_adapters.self_test |
| `hhs_runtime/hhs_guarded_plugin_invocation_executor_v1.py` | `hhs_runtime.hhs_guarded_plugin_invocation_executor_v1` | registered guarded service: guarded_plugin_invocation_executor.self_test |
| `hhs_runtime/hhs_hash72_kernel_authority_v1.py` | `hhs_runtime.hhs_hash72_kernel_authority_v1` | registered guarded service: hash72.kernel_authority_self_test |
| `hhs_runtime/hhs_io_gateway_v1.py` | `hhs_runtime.hhs_io_gateway_v1` | registered guarded service: io_gateway.self_test |
| `hhs_runtime/hhs_persistence_guard_v1.py` | `hhs_runtime.hhs_persistence_guard_v1` | registered guarded service: persistence.guard_self_test |
| `hhs_runtime/hhs_plugin_capability_planner_v1.py` | `hhs_runtime.hhs_plugin_capability_planner_v1` | registered guarded service: plugin_capability_planner.self_test |
| `hhs_runtime/hhs_receipt_vector_index_v1.py` | `hhs_runtime.hhs_receipt_vector_index_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_runtime/hhs_recursive_global_constraint_bundle_v1.py` | `hhs_runtime.hhs_recursive_global_constraint_bundle_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_runtime/hhs_recursive_symbol_kernel_v1.py` | `hhs_runtime.hhs_recursive_symbol_kernel_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_runtime/hhs_runtime_contract_v1.py` | `hhs_runtime.hhs_runtime_contract_v1` | registered guarded service: runtime_contract.self_test |
| `hhs_runtime/hhs_runtime_dataflow_guard_v1.py` | `hhs_runtime.hhs_runtime_dataflow_guard_v1` | registered guarded service: runtime_dataflow.guard_self_test |
| `hhs_runtime/hhs_runtime_integration_decisions_v1.py` | `hhs_runtime.hhs_runtime_integration_decisions_v1` | registered guarded service: runtime_integration.decisions_self_test |
| `hhs_runtime/hhs_runtime_reachability_audit_v1.py` | `hhs_runtime.hhs_runtime_reachability_audit_v1` | registered guarded service: runtime_reachability.audit_self_test |
| `hhs_runtime/hhs_semantic_memory_guard_v1.py` | `hhs_runtime.hhs_semantic_memory_guard_v1` | registered guarded service: semantic_memory.guard_self_test |
| `hhs_runtime/hhs_semantic_plugin_adapter_runtime_v1.py` | `hhs_runtime.hhs_semantic_plugin_adapter_runtime_v1` | registered guarded service: semantic_plugin_adapter_runtime.self_test |
| `hhs_runtime/hhs_srcg_gate_v1.py` | `hhs_runtime.hhs_srcg_gate_v1` | registered guarded service: srcg.primitive_self_test, srcg.selfsolve_ab_gate |
| `hhs_runtime/hhs_symbolic_quantum_algebra_v1.py` | `hhs_runtime.hhs_symbolic_quantum_algebra_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_runtime/hhs_system_closure_harness_v1.py` | `hhs_runtime.hhs_system_closure_harness_v1` | registered guarded service: system_closure.harness_self_test |
| `hhs_runtime/hhs_text_semantic_reconstruction_v1.py` | `hhs_runtime.hhs_text_semantic_reconstruction_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_runtime/hhs_unified_hash72_ledger_v1.py` | `hhs_runtime.hhs_unified_hash72_ledger_v1` | registered guarded service: ledger.verify |
| `hhs_runtime/hhs_wordnet_relation_enforcer_v1.py` | `hhs_runtime.hhs_wordnet_relation_enforcer_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_self_solving_constraint_modules_v1.py` | `hhs_self_solving_constraint_modules_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |
| `hhs_self_solving_constraint_pipeline_v1.py` | `hhs_self_solving_constraint_pipeline_v1` | Pass 025 integration decision: wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared |


## API_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `hhs_backend/api/runtime_routes.py` | `hhs_backend.api.runtime_routes` | reachable through canonical backend/API route graph |
| `hhs_backend/server.py` | `hhs_backend.server` | reachable through canonical backend/API route graph |
| `hhs_graph/hhs_multimodal_receipt_graph_v1.py` | `hhs_graph.hhs_multimodal_receipt_graph_v1` | reachable through canonical backend/API route graph |
| `hhs_python/runtime/hhs_runtime_controller.py` | `hhs_python.runtime.hhs_runtime_controller` | reachable through canonical backend/API route graph |
| `hhs_python/runtime/hhs_runtime_emulator.py` | `hhs_python.runtime.hhs_runtime_emulator` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_filesystem_hash72_ledger_v1.py` | `hhs_runtime.hhs_filesystem_hash72_ledger_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_loshu_phase_embedding_v1.py` | `hhs_runtime.hhs_loshu_phase_embedding_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_repo_paths_v1.py` | `hhs_runtime.hhs_repo_paths_v1` | reachable through canonical backend/API route graph |
| `hhs_runtime/hhs_service_registry_v1.py` | `hhs_runtime.hhs_service_registry_v1` | reachable through canonical backend/API route graph |


## GUI_REACHABLE

| Path | Module | Reason |
|---|---|---|
| `hhs_gui/main.tsx` | `hhs_gui.main` | frontend runtime/contract surface |
| `hhs_gui/src/App.tsx` | `hhs_gui.src.App` | frontend runtime/contract surface |


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
| `hhs_backend/runtime/runtime_adaptive_goal_engine.py` | `hhs_backend.runtime.runtime_adaptive_goal_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_agentic_cognition_layer.py` | `hhs_backend.runtime.runtime_agentic_cognition_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_autonomous_research_layer.py` | `hhs_backend.runtime.runtime_autonomous_research_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_event_bus.py` | `hhs_backend.runtime.runtime_event_bus` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_event_schema.py` | `hhs_backend.runtime.runtime_event_schema` | source has integration shape but no current guarded route/service |
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
| `hhs_backend/runtime/runtime_ws.py` | `hhs_backend.runtime.runtime_ws` | Pass 025 integration decision: legacy/high-value source retained for guarded adapter integration; no direct execution authorized |
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
| `hhs_gui/runtime_os/core/RuntimeApplicationRegistry.tsx` | `hhs_gui.runtime_os.core.RuntimeApplicationRegistry` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeCommandBar.tsx` | `hhs_gui.runtime_os.core.RuntimeCommandBar` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeCommandPalette.tsx` | `hhs_gui.runtime_os.core.RuntimeCommandPalette` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeConsole.tsx` | `hhs_gui.runtime_os.core.RuntimeConsole` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeContractEnvelope.ts` | `hhs_gui.runtime_os.core.RuntimeContractEnvelope` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeDesktop.tsx` | `hhs_gui.runtime_os.core.RuntimeDesktop` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeDock.tsx` | `hhs_gui.runtime_os.core.RuntimeDock` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeExecutionAuthority.ts` | `hhs_gui.runtime_os.core.RuntimeExecutionAuthority` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeGraphOverlay.tsx` | `hhs_gui.runtime_os.core.RuntimeGraphOverlay` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeGraphRenderer.tsx` | `hhs_gui.runtime_os.core.RuntimeGraphRenderer` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeKernelBridge.ts` | `hhs_gui.runtime_os.core.RuntimeKernelBridge` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeOS.ts` | `hhs_gui.runtime_os.core.RuntimeOS` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeRouter.ts` | `hhs_gui.runtime_os.core.RuntimeRouter` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeSession.ts` | `hhs_gui.runtime_os.core.RuntimeSession` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeShell.tsx` | `hhs_gui.runtime_os.core.RuntimeShell` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeSidebar.tsx` | `hhs_gui.runtime_os.core.RuntimeSidebar` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeSocketManager.ts` | `hhs_gui.runtime_os.core.RuntimeSocketManager` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeStateStore.ts` | `hhs_gui.runtime_os.core.RuntimeStateStore` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeTopbar.tsx` | `hhs_gui.runtime_os.core.RuntimeTopbar` | frontend source not yet explicitly mapped to runtime bridge |
| … | … | 248 additional records omitted from this summary; see JSON manifest. |


## ORPHAN Candidates

These require explicit integration, deprecation, or documentation-only classification in subsequent passes.

| Path | Module | Reason |
|---|---|---|
| — | — | — |


## Kernel Witness

The manifest itself is sealed with a C `u^72` Digital DNA Hash72 kernel witness.

```json
{
  "canonical_payload": "\"{\\\"api_route_count\\\": 18, \\\"orphan_count\\\": 0, \\\"record_count\\\": 677, \\\"schema\\\": \\\"HHS_RUNTIME_REACHABILITY_MANIFEST_V1\\\", \\\"service_count\\\": 19, \\\"status_counts\\\": {\\\"API_REACHABLE\\\": 9, \\\"BOOT_REACHABLE\\\": 14, \\\"DOCUMENTED_ONLY\\\": 275, \\\"GUI_REACHABLE\\\": 2, \\\"PLUGIN_READY\\\": 348, \\\"SERVICE_REACHABLE\\\": 29}, \\\"version\\\": \\\"PASS_025\\\"}\"",
  "digest": "A9foFMKE7<2*T+qjz((OkIg3lUyJHMEV/RY?RKbGvOXa83uCg*trkpcAd<1Nz52KYToQ<JCB",
  "dna": "A9foFMKE7<2*T+qjz((OkIg3lUyJHMEV/RY?RKbGvOXa83uCg*trkpcAd<1Nz52KYToQ<JCB",
  "label": "hhs_runtime_reachability_manifest_v1",
  "positions": [
    36,
    9,
    15,
    24,
    41,
    48,
    46,
    40,
    7,
    68,
    2,
    64,
    55,
    63,
    26,
    19,
    35,
    66,
    66,
    50,
    20,
    44,
    16,
    3,
    21,
    56,
    34,
    45,
    43,
    48,
    40,
    57,
    65,
    53,
    60,
    71,
    53,
    46,
    11,
    42,
    31,
    50,
    59,
    10,
    8,
    3,
    30,
    38,
    16,
    64,
    29,
    27,
    20,
    25,
    12,
    36,
    13,
    68,
    1,
    49,
    35,
    5,
    2,
    46,
    60,
    55,
    24,
    52,
    68,
    45,
    38,
    37
  ],
  "rotation_profile": [
    -36,
    -136,
    157,
    21,
    -107,
    -29,
    112,
    -39,
    -1,
    -13,
    64,
    -19,
    43,
    -22,
    12,
    -68,
    19,
    49,
    -24,
    -41,
    0,
    23,
    -6,
    -20,
    -3,
    31,
    8,
    18,
    15,
    -53,
    82,
    -190,
    33,
    20,
    -118,
    108,
    89,
    9,
    45,
    -213,
    63,
    81,
    -127,
    183,
    -180,
    102,
    56,
    -81,
    -32,
    15,
    51,
    -96,
    40,
    44,
    -42,
    -91,
    101,
    11,
    -57,
    62,
    47,
    -56,
    12,
    -89,
    -4,
    134,
    -114,
    129,
    -72,
    -24,
    112,
    2
  ],
  "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
  "trace_count": 379,
  "zero_sum": true
}
```
