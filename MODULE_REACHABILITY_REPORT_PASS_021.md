# Module Reachability Report — Pass 021

## Purpose

Pass 021 establishes the repository-wide runtime truth map. Every source-like module is classified by how it enters the HHS validated execution graph, or by why it is intentionally not executable.

## Status Counts

```json
{
  "API_REACHABLE": 9,
  "BOOT_REACHABLE": 14,
  "DOCUMENTED_ONLY": 195,
  "GUI_REACHABLE": 2,
  "ORPHAN": 291,
  "PLUGIN_READY": 104,
  "SERVICE_REACHABLE": 13
}
```

## Canonical Surfaces

- Services discovered: **14**
- API routes discovered: **18**
- GUI runtime surfaces discovered: **2**
- Orphan records: **291**
- Plugin-ready candidates: **104**

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
| `hhs_foundation/hhs_foundational_standards_v1.py` | `hhs_foundation.hhs_foundational_standards_v1` | registered guarded service: foundational_standards.self_test |
| `hhs_python/runtime/hhs_ctypes_bridge.py` | `hhs_python.runtime.hhs_ctypes_bridge` | registered guarded service: c_bridge.abi_self_test |
| `hhs_runtime/hhs_authority_gate_v1.py` | `hhs_runtime.hhs_authority_gate_v1` | registered guarded service: authority_gate.self_test |
| `hhs_runtime/hhs_hash72_kernel_authority_v1.py` | `hhs_runtime.hhs_hash72_kernel_authority_v1` | registered guarded service: hash72.kernel_authority_self_test |
| `hhs_runtime/hhs_io_gateway_v1.py` | `hhs_runtime.hhs_io_gateway_v1` | registered guarded service: io_gateway.self_test |
| `hhs_runtime/hhs_persistence_guard_v1.py` | `hhs_runtime.hhs_persistence_guard_v1` | registered guarded service: persistence.guard_self_test |
| `hhs_runtime/hhs_runtime_contract_v1.py` | `hhs_runtime.hhs_runtime_contract_v1` | registered guarded service: runtime_contract.self_test |
| `hhs_runtime/hhs_runtime_dataflow_guard_v1.py` | `hhs_runtime.hhs_runtime_dataflow_guard_v1` | registered guarded service: runtime_dataflow.guard_self_test |
| `hhs_runtime/hhs_runtime_reachability_audit_v1.py` | `hhs_runtime.hhs_runtime_reachability_audit_v1` | registered guarded service: runtime_reachability.audit_self_test |
| `hhs_runtime/hhs_semantic_memory_guard_v1.py` | `hhs_runtime.hhs_semantic_memory_guard_v1` | registered guarded service: semantic_memory.guard_self_test |
| `hhs_runtime/hhs_srcg_gate_v1.py` | `hhs_runtime.hhs_srcg_gate_v1` | registered guarded service: srcg.primitive_self_test, srcg.selfsolve_ab_gate |
| `hhs_runtime/hhs_system_closure_harness_v1.py` | `hhs_runtime.hhs_system_closure_harness_v1` | registered guarded service: system_closure.harness_self_test |
| `hhs_runtime/hhs_unified_hash72_ledger_v1.py` | `hhs_runtime.hhs_unified_hash72_ledger_v1` | registered guarded service: ledger.verify |


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
| `hhs_backend/runtime/distributed_consensus_runtime.py` | `hhs_backend.runtime.distributed_consensus_runtime` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/distributed_runtime_node_v1.py` | `hhs_backend.runtime.distributed_runtime_node_v1` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_adaptive_goal_engine.py` | `hhs_backend.runtime.runtime_adaptive_goal_engine` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_agentic_cognition_layer.py` | `hhs_backend.runtime.runtime_agentic_cognition_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_autonomous_research_layer.py` | `hhs_backend.runtime.runtime_autonomous_research_layer` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_event_bus.py` | `hhs_backend.runtime.runtime_event_bus` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_event_schema.py` | `hhs_backend.runtime.runtime_event_schema` | source has integration shape but no current guarded route/service |
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
| `hhs_backend/runtime/runtime_snapshot_codec.py` | `hhs_backend.runtime.runtime_snapshot_codec` | source has integration shape but no current guarded route/service |
| `hhs_backend/runtime/runtime_transport_protocol.py` | `hhs_backend.runtime.runtime_transport_protocol` | source has integration shape but no current guarded route/service |
| `hhs_backend/websocket/runtime_stream_manager.py` | `hhs_backend.websocket.runtime_stream_manager` | source has integration shape but no current guarded route/service |
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
| `hhs_gui/runtime_os/core/RuntimeViewport.tsx` | `hhs_gui.runtime_os.core.RuntimeViewport` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeWindowContent.tsx` | `hhs_gui.runtime_os.core.RuntimeWindowContent` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeWindowManager.ts` | `hhs_gui.runtime_os.core.RuntimeWindowManager` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeWindowManager.tsx` | `hhs_gui.runtime_os.core.RuntimeWindowManager` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/core/RuntimeWorkspace.ts` | `hhs_gui.runtime_os.core.RuntimeWorkspace` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/graph/RuntimeGraphProjectionEngine.ts` | `hhs_gui.runtime_os.graph.RuntimeGraphProjectionEngine` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/state/RuntimeStateStore.ts` | `hhs_gui.runtime_os.state.RuntimeStateStore` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/state/RuntimeWorkspacePersistence.ts` | `hhs_gui.runtime_os.state.RuntimeWorkspacePersistence` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/workspace/HHSRuntimeSpatialOrchestrator.tsx` | `hhs_gui.runtime_os.workspace.HHSRuntimeSpatialOrchestrator` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/runtime_os/workspace/HHSUnifiedWorkspace.tsx` | `hhs_gui.runtime_os.workspace.HHSUnifiedWorkspace` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/src/components/RuntimeShell.tsx` | `hhs_gui.src.components.RuntimeShell` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/src/main.tsx` | `hhs_gui.src.main` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/tailwind.config.ts` | `hhs_gui.tailwind.config` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_gui/vite.config.ts` | `hhs_gui.vite.config` | frontend source not yet explicitly mapped to runtime bridge |
| `hhs_python/runtime/hhs_runtime_object.py` | `hhs_python.runtime.hhs_runtime_object` | source has integration shape but no current guarded route/service |
| `hhs_python/runtime/runtime_object_registry.py` | `hhs_python.runtime.runtime_object_registry` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_attention_operator_v1.py` | `hhs_runtime.hhs_attention_operator_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_audio_language_adapter_v1.py` | `hhs_runtime.hhs_audio_language_adapter_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_branch_rejoin_operator_v1.py` | `hhs_runtime.hhs_branch_rejoin_operator_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_constraint_branch_router_v1.py` | `hhs_runtime.hhs_constraint_branch_router_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_degrees_of_freedom_guard_v1.py` | `hhs_runtime.hhs_degrees_of_freedom_guard_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_drive_corpus_ingestion_engine_v1.py` | `hhs_runtime.hhs_drive_corpus_ingestion_engine_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_execution_router_v1.py` | `hhs_runtime.hhs_execution_router_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_goal_attractor_engine_v1.py` | `hhs_runtime.hhs_goal_attractor_engine_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_goal_oriented_planning_engine_v1.py` | `hhs_runtime.hhs_goal_oriented_planning_engine_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_invariant_receipt_bridge_v1.py` | `hhs_runtime.hhs_invariant_receipt_bridge_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_language_runtime_validator_cli_v1.py` | `hhs_runtime.hhs_language_runtime_validator_cli_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_linguistic_operator_training_loop_v1.py` | `hhs_runtime.hhs_linguistic_operator_training_loop_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_manifold_ledger_v1.py` | `hhs_runtime.hhs_manifold_ledger_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_memory_ledger_replay_v1.py` | `hhs_runtime.hhs_memory_ledger_replay_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_multi_agent_operator_orchestrator_v1.py` | `hhs_runtime.hhs_multi_agent_operator_orchestrator_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_operator_execution_layer_v1.py` | `hhs_runtime.hhs_operator_execution_layer_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_operator_selection_engine_v1.py` | `hhs_runtime.hhs_operator_selection_engine_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_phase_coherent_operator_loop_v1.py` | `hhs_runtime.hhs_phase_coherent_operator_loop_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_python_bridge.py` | `hhs_runtime.hhs_python_bridge` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_qgu_temporal_phase_guard_v1.py` | `hhs_runtime.hhs_qgu_temporal_phase_guard_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_runtime/hhs_python_bridge.py` | `hhs_runtime.hhs_runtime.hhs_python_bridge` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_symbolic_linguistic_substitution_solver_v1.py` | `hhs_runtime.hhs_symbolic_linguistic_substitution_solver_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_symbolic_reasoning_engine_v1.py` | `hhs_runtime.hhs_symbolic_reasoning_engine_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/hhs_symbolic_selection_memory_adapter_v1.py` | `hhs_runtime.hhs_symbolic_selection_memory_adapter_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime/runtime_lock_certifier_v1.py` | `hhs_runtime.runtime_lock_certifier_v1` | source has integration shape but no current guarded route/service |
| `hhs_runtime_state.py` | `hhs_runtime_state` | source has integration shape but no current guarded route/service |
| `hhs_storage/runtime_state_store_v1.py` | `hhs_storage.runtime_state_store_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_backend_guarded_routes_v1.py` | `tests.test_hhs_backend_guarded_routes_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_foundational_standards_v1.py` | `tests.test_hhs_foundational_standards_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_hash72_kernel_authority_v1.py` | `tests.test_hhs_hash72_kernel_authority_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_persistence_guard_v1.py` | `tests.test_hhs_persistence_guard_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_runtime_contract_v1.py` | `tests.test_hhs_runtime_contract_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_runtime_dataflow_guard_v1.py` | `tests.test_hhs_runtime_dataflow_guard_v1` | source has integration shape but no current guarded route/service |
| `tests/test_hhs_runtime_reachability_audit_v1.py` | `tests.test_hhs_runtime_reachability_audit_v1` | source has integration shape but no current guarded route/service |
| … | … | 4 additional records omitted from this summary; see JSON manifest. |


## ORPHAN Candidates

These require explicit integration, deprecation, or documentation-only classification in subsequent passes.

| Path | Module | Reason |
|---|---|---|
| `.github/workflows/hhs-acceptance-gate.yml` | `.github.workflows.hhs-acceptance-gate` | no boot/service/API/GUI/static documentation reachability found |
| `EXECUTION_GRAPH_PASS_021.json` | `EXECUTION_GRAPH_PASS_021` | no boot/service/API/GUI/static documentation reachability found |
| `HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py` | `HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7` | no boot/service/API/GUI/static documentation reachability found |
| `RUNTIME_REACHABILITY_MANIFEST.json` | `RUNTIME_REACHABILITY_MANIFEST` | no boot/service/API/GUI/static documentation reachability found |
| `WordnetThesaurus.csv` | `WordnetThesaurus` | no boot/service/API/GUI/static documentation reachability found |
| `data/runtime/hhs_filesystem_ledger.json` | `data.runtime.hhs_filesystem_ledger` | no boot/service/API/GUI/static documentation reachability found |
| `data/runtime/hhs_unified_hash72_ledger.json` | `data.runtime.hhs_unified_hash72_ledger` | no boot/service/API/GUI/static documentation reachability found |
| `data/runtime/persistence_guard_self_test.json` | `data.runtime.persistence_guard_self_test` | no boot/service/API/GUI/static documentation reachability found |
| `data/runtime/persistence_guard_self_test.txt` | `data.runtime.persistence_guard_self_test` | no boot/service/API/GUI/static documentation reachability found |
| `examples/hhs_loshu_phase_embedding_demo_v1.py` | `examples.hhs_loshu_phase_embedding_demo_v1` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/package.json` | `gui.hhs-mobile-runtime-console.package` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/App.tsx` | `gui.hhs-mobile-runtime-console.src.App` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/api/hhsApi.ts` | `gui.hhs-mobile-runtime-console.src.api.hhsApi` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/audioPhaseClient.ts` | `gui.hhs-mobile-runtime-console.src.audioPhaseClient` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/calculatorExpressionModel.ts` | `gui.hhs-mobile-runtime-console.src.calculatorExpressionModel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/AlertPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.AlertPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/AssistantWorkspace.tsx` | `gui.hhs-mobile-runtime-console.src.components.AssistantWorkspace` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.CalculatorPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanelV2.tsx` | `gui.hhs-mobile-runtime-console.src.components.CalculatorPanelV2` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/CertificationPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.CertificationPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/ExecutionPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.ExecutionPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/IntentBar.tsx` | `gui.hhs-mobile-runtime-console.src.components.IntentBar` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/LedgerPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.LedgerPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/OperatorPanel.tsx` | `gui.hhs-mobile-runtime-console.src.components.OperatorPanel` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/PhaseRing3D.tsx` | `gui.hhs-mobile-runtime-console.src.components.PhaseRing3D` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/ReceiptStream.tsx` | `gui.hhs-mobile-runtime-console.src.components.ReceiptStream` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/RuntimeTelemetry.tsx` | `gui.hhs-mobile-runtime-console.src.components.RuntimeTelemetry` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/components/StatusHeader.tsx` | `gui.hhs-mobile-runtime-console.src.components.StatusHeader` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/displayPhaseAnalysis.ts` | `gui.hhs-mobile-runtime-console.src.displayPhaseAnalysis` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/hooks/useHHSStream.ts` | `gui.hhs-mobile-runtime-console.src.hooks.useHHSStream` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/hooks/useRuntime.ts` | `gui.hhs-mobile-runtime-console.src.hooks.useRuntime` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/main.tsx` | `gui.hhs-mobile-runtime-console.src.main` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/runtimeData.ts` | `gui.hhs-mobile-runtime-console.src.runtimeData` | no boot/service/API/GUI/static documentation reachability found |
| `gui/hhs-mobile-runtime-console/src/useCalculatorDoc.ts` | `gui.hhs-mobile-runtime-console.src.useCalculatorDoc` | no boot/service/API/GUI/static documentation reachability found |
| `harmonicode_agent_v43_3_dna_lockcore_patched_selfsolving_hash72authority_locked-7.py` | `harmonicode_agent_v43_3_dna_lockcore_patched_selfsolving_hash72authority_locked-7` | no boot/service/API/GUI/static documentation reachability found |
| `harmonicode_modality_verbatim_ingestion_v1-1.py` | `harmonicode_modality_verbatim_ingestion_v1-1` | no boot/service/API/GUI/static documentation reachability found |
| `harmonicode_verbatim_semantic_database_v1.py` | `harmonicode_verbatim_semantic_database_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_backend/__init__.py` | `hhs_backend` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_backend/runtime/runtime_graph_projection.py` | `hhs_backend.runtime.runtime_graph_projection` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_backend/runtime/runtime_server.py` | `hhs_backend.runtime.runtime_server` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_backend/runtime/runtime_ws.py` | `hhs_backend.runtime.runtime_ws` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_backend_final_certification_v1.py` | `hhs_backend_final_certification_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_control_flow_gates_v1.py` | `hhs_control_flow_gates_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_database_integration_layer_v1.py` | `hhs_database_integration_layer_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_execution_geometry_v1.py` | `hhs_execution_geometry_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M001.py` | `hhs_foundation.HHS-M001` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M002.py` | `hhs_foundation.HHS-M002` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M003.py` | `hhs_foundation.HHS-M003` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M004.py` | `hhs_foundation.HHS-M004` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M005.py` | `hhs_foundation.HHS-M005` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M006.py` | `hhs_foundation.HHS-M006` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS-M007.py` | `hhs_foundation.HHS-M007` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M001.py` | `hhs_foundation.HHS_M001` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M002.py` | `hhs_foundation.HHS_M002` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M003.py` | `hhs_foundation.HHS_M003` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M004.py` | `hhs_foundation.HHS_M004` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M005.py` | `hhs_foundation.HHS_M005` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M006.py` | `hhs_foundation.HHS_M006` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/HHS_M007.py` | `hhs_foundation.HHS_M007` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/__init__.py` | `hhs_foundation` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/constitutional_validator.py` | `hhs_foundation.constitutional_validator` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_foundation/meaning_conservation.py` | `hhs_foundation.meaning_conservation` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_general_runtime_layer_v1.py` | `hhs_general_runtime_layer_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_gui/package.json` | `hhs_gui.package` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_gui/tsconfig.json` | `hhs_gui.tsconfig` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_gui/tsconfig.node.json` | `hhs_gui.tsconfig.node` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_hash_commitment_layer.py` | `hhs_hash_commitment_layer` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_input_bridge_v1.py` | `hhs_input_bridge_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_physics_evolution_v1.py` | `hhs_physics_evolution_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_physics_model_v1.py` | `hhs_physics_model_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_program_format_and_cli_v1.py` | `hhs_program_format_and_cli_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_adaptive_correction_field.py` | `hhs_python.runtime.hhs_adaptive_correction_field` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_autonomous_manifold_governor.py` | `hhs_python.runtime.hhs_autonomous_manifold_governor` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_causal_consistency_kernel.py` | `hhs_python.runtime.hhs_causal_consistency_kernel` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_causality_manifold.py` | `hhs_python.runtime.hhs_causality_manifold` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_distributed_reversibility_mesh.py` | `hhs_python.runtime.hhs_distributed_reversibility_mesh` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_entangled_state_transport_mesh.py` | `hhs_python.runtime.hhs_entangled_state_transport_mesh` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_event_schema.py` | `hhs_python.runtime.hhs_event_schema` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_global_reversibility_gate.py` | `hhs_python.runtime.hhs_global_reversibility_gate` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_invariant_consensus_engine.py` | `hhs_python.runtime.hhs_invariant_consensus_engine` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_multimodal_projection_manifold.py` | `hhs_python.runtime.hhs_multimodal_projection_manifold` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_multimodal_projection_orchestrator.py` | `hhs_python.runtime.hhs_multimodal_projection_orchestrator` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_multimodal_transition_tensor81.py` | `hhs_python.runtime.hhs_multimodal_transition_tensor81` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_projection_surface_protocol.py` | `hhs_python.runtime.hhs_projection_surface_protocol` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_recursive_consensus_constellation.py` | `hhs_python.runtime.hhs_recursive_consensus_constellation` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_recursive_manifold_memory_ledger.py` | `hhs_python.runtime.hhs_recursive_manifold_memory_ledger` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_recursive_origin_anchor.py` | `hhs_python.runtime.hhs_recursive_origin_anchor` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_recursive_phase_compiler.py` | `hhs_python.runtime.hhs_recursive_phase_compiler` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_replay_projection_field.py` | `hhs_python.runtime.hhs_replay_projection_field` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_runtime_identity_field.py` | `hhs_python.runtime.hhs_runtime_identity_field` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_runtime_observability_manifold.py` | `hhs_python.runtime.hhs_runtime_observability_manifold` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_runtime_orchestrator.py` | `hhs_python.runtime.hhs_runtime_orchestrator` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_runtime_state.py` | `hhs_python.runtime.hhs_runtime_state` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_semantic_readability_oracle.py` | `hhs_python.runtime.hhs_semantic_readability_oracle` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_temporal_invariant_lattice.py` | `hhs_python.runtime.hhs_temporal_invariant_lattice` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_tensor81_execution_lattice.py` | `hhs_python.runtime.hhs_tensor81_execution_lattice` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_universal_mutation_contract.py` | `hhs_python.runtime.hhs_universal_mutation_contract` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_python/runtime/hhs_universal_reversibility_adjudicator.py` | `hhs_python.runtime.hhs_universal_reversibility_adjudicator` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_realtime_phase_certification_v1.py` | `hhs_realtime_phase_certification_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_receipt_replay_verifier_v1.py` | `hhs_receipt_replay_verifier_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_regression_suite_v1.py` | `hhs_regression_suite_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/English_Word_List.txt` | `hhs_runtime.English_Word_List` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/Grammar Correction.csv` | `hhs_runtime.Grammar Correction` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetAdjectives.csv` | `hhs_runtime.WordnetAdjectives` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetAdverbs.csv` | `hhs_runtime.WordnetAdverbs` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetAntonyms.csv` | `hhs_runtime.WordnetAntonyms` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetHypernyms.csv` | `hhs_runtime.WordnetHypernyms` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetHyponyms.csv` | `hhs_runtime.WordnetHyponyms` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetNouns.csv` | `hhs_runtime.WordnetNouns` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetSynonyms.csv` | `hhs_runtime.WordnetSynonyms` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/WordnetVerbs.csv` | `hhs_runtime.WordnetVerbs` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/__init__.py` | `hhs_runtime` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/acceleration/HHSAccelerationFabric.ts` | `hhs_runtime.acceleration.HHSAccelerationFabric` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core/hash72_validator_v1.py` | `hhs_runtime.core.hash72_validator_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/__init__.py` | `hhs_runtime.core_sandbox` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/adversarial_complex_v2.py` | `hhs_runtime.core_sandbox.adversarial_complex_v2` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/adversarial_parallel_v1.py` | `hhs_runtime.core_sandbox.adversarial_parallel_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/adversarial_parallel_with_rejects_v1.py` | `hhs_runtime.core_sandbox.adversarial_parallel_with_rejects_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/adversarial_test_v1.py` | `hhs_runtime.core_sandbox.adversarial_test_v1` | no boot/service/API/GUI/static documentation reachability found |
| `hhs_runtime/core_sandbox/deep_test_v1.py` | `hhs_runtime.core_sandbox.deep_test_v1` | no boot/service/API/GUI/static documentation reachability found |
| … | … | 171 additional records omitted from this summary; see JSON manifest. |


## Kernel Witness

The manifest itself is sealed with a C `u^72` Digital DNA Hash72 kernel witness.

```json
{
  "canonical_payload": "\"{\\\"api_route_count\\\": 18, \\\"orphan_count\\\": 291, \\\"record_count\\\": 628, \\\"schema\\\": \\\"HHS_RUNTIME_REACHABILITY_MANIFEST_V1\\\", \\\"service_count\\\": 14, \\\"status_counts\\\": {\\\"API_REACHABLE\\\": 9, \\\"BOOT_REACHABLE\\\": 14, \\\"DOCUMENTED_ONLY\\\": 195, \\\"GUI_REACHABLE\\\": 2, \\\"ORPHAN\\\": 291, \\\"PLUGIN_READY\\\": 104, \\\"SERVICE_REACHABLE\\\": 13}, \\\"version\\\": \\\"PASS_021\\\"}\"",
  "digest": "fcye-1F)f/+-DkEizywP5s+q>(-WMlHVZjyeAKP<T)??6FWj4eFGpLr7g*G)8TfKasZ/x/H0",
  "dna": "fcye-1F)f/+-DkEizywP5s+q>(-WMlHVZjyeAKP<T)??6FWj4eFGpLr7g*G)8TfKasZ/x/H0",
  "label": "hhs_runtime_reachability_manifest_v1",
  "positions": [
    15,
    12,
    34,
    14,
    62,
    1,
    41,
    67,
    15,
    65,
    63,
    62,
    39,
    20,
    40,
    18,
    35,
    34,
    32,
    51,
    5,
    28,
    63,
    26,
    69,
    66,
    62,
    58,
    48,
    21,
    43,
    57,
    61,
    19,
    34,
    14,
    36,
    46,
    51,
    68,
    55,
    67,
    71,
    71,
    6,
    41,
    58,
    19,
    4,
    14,
    41,
    42,
    25,
    47,
    27,
    7,
    16,
    64,
    42,
    67,
    8,
    55,
    15,
    46,
    10,
    28,
    61,
    65,
    33,
    65,
    43,
    0
  ],
  "rotation_profile": [
    87,
    11,
    -40,
    -133,
    202,
    -4,
    -109,
    -12,
    7,
    56,
    53,
    -93,
    99,
    7,
    -46,
    3,
    19,
    -55,
    14,
    32,
    -15,
    7,
    -31,
    75,
    -27,
    -31,
    36,
    -113,
    20,
    64,
    -59,
    26,
    29,
    -14,
    0,
    -93,
    0,
    81,
    13,
    -43,
    15,
    -46,
    -43,
    100,
    -110,
    68,
    12,
    -28,
    28,
    -107,
    63,
    -81,
    117,
    -78,
    45,
    24,
    -40,
    7,
    56,
    8,
    -52,
    -6,
    97,
    -17,
    -54,
    -109,
    67,
    142,
    -107,
    140,
    -99,
    -35
  ],
  "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
  "trace_count": 398,
  "zero_sum": true
}
```
