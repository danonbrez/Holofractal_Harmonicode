# Runtime Integration Decisions — Pass 023

## Purpose

Pass 023 updates integration decisions after the first guarded static adapter batch converts selected plugin-ready files into explicit release decisions. This is not deletion and not semantic rewriting. It is the first controlled reduction of the orphan frontier created in Pass 021.

## Decision Counts

```json
{
  "DOCUMENTED_ONLY": 176,
  "PLUGIN_READY": 368,
  "WIRED": 13
}
```

## Policy

No source-like file may remain silently outside the validated runtime graph. Each candidate must become one of:

- `WIRED`
- `PLUGIN_READY`
- `DOCUMENTED_ONLY`
- `DEPRECATED`

## PLUGIN_READY

These files are retained as high-value integration candidates. They are not authorized for direct execution until wrapped by the service registry, API contract, GUI bridge, or plugin SDK.

| Path | Reason | Guarded Entry Required |
|---|---|---|
| `HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `examples/hhs_loshu_phase_embedding_demo_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/App.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/api/hhsApi.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/audioPhaseClient.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/calculatorExpressionModel.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/AlertPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/AssistantWorkspace.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/CalculatorPanelV2.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/CertificationPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/ExecutionPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/IntentBar.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/LedgerPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/OperatorPanel.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/PhaseRing3D.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/ReceiptStream.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/RuntimeTelemetry.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/components/StatusHeader.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/displayPhaseAnalysis.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/hooks/useHHSStream.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/hooks/useRuntime.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/main.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/runtimeData.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `gui/hhs-mobile-runtime-console/src/useCalculatorDoc.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `harmonicode_agent_v43_3_dna_lockcore_patched_selfsolving_hash72authority_locked-7.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/api/runtime_routes.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/distributed_consensus_runtime.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/distributed_runtime_node_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_adaptive_goal_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_agentic_cognition_layer.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_autonomous_research_layer.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_event_bus.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_event_schema.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_graph_projection.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_multimodal_embedding_router.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_multinode_goal_consensus.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_orchestrator.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_prediction_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_receipt_chain.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_recursive_toolchain_layer.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_rehydration_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_replay_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_replay_topology.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_self_modification_governor.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_semantic_memory_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_server.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_snapshot_codec.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_transport_protocol.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/runtime/runtime_ws.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend/websocket/runtime_stream_manager.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_backend_final_certification_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_control_flow_gates_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_execution_geometry_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_foundation/HHS-M001.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M002.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M003.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M004.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M005.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M006.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS-M007.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M001.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M002.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M003.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M004.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M005.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M006.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/HHS_M007.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/__init__.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/constitutional_validator.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_foundation/hhs_foundational_standards_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_foundation/meaning_conservation.py` | constitutional compatibility shim; callable only through canonical foundational standards module | `True` |
| `hhs_general_runtime_layer_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_graph/hhs_multimodal_receipt_graph_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/main.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/postcss.config.js` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime/runtime_workspace_objects.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/breadboard/HHSRuntimeBreadboard.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/breadboard/HHSRuntimeTransportOverlay.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/breadboard/RuntimeBreadboard.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/calculator/HHSCalculatorGraphProjection.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/calculator/HHSCalculatorSurface.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/calculator/RuntimeCalculator.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/instruments/ReceiptInspector.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_apps/instruments/ReplayTimeline.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeApplicationRegistry.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeCommandBar.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeCommandPalette.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeConsole.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeContractEnvelope.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeDesktop.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeDock.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeExecutionAuthority.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeGraphOverlay.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeGraphRenderer.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeKernelBridge.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeOS.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeRouter.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeSession.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeShell.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeSidebar.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeSocketManager.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeStateStore.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeTopbar.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeViewport.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeWindowContent.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeWindowManager.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeWindowManager.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/core/RuntimeWorkspace.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/graph/RuntimeGraphProjectionEngine.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/state/RuntimeStateStore.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/state/RuntimeWorkspacePersistence.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/workspace/HHSRuntimeSpatialOrchestrator.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/runtime_os/workspace/HHSUnifiedWorkspace.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/src/App.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/src/components/RuntimeShell.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/src/main.tsx` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_gui/tailwind.config.ts` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_hash_commitment_layer.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_input_bridge_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_physics_evolution_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_physics_model_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_program_format_and_cli_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_adaptive_correction_field.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_autonomous_manifold_governor.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_causal_consistency_kernel.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_causality_manifold.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_ctypes_bridge.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_distributed_reversibility_mesh.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_entangled_state_transport_mesh.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_event_schema.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_global_reversibility_gate.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_invariant_consensus_engine.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_multimodal_projection_manifold.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_multimodal_projection_orchestrator.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_multimodal_transition_tensor81.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_projection_surface_protocol.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_recursive_consensus_constellation.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_recursive_manifold_memory_ledger.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_recursive_origin_anchor.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_recursive_phase_compiler.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_replay_projection_field.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_controller.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_emulator.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_identity_field.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_object.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_observability_manifold.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_orchestrator.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_runtime_state.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_semantic_readability_oracle.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_temporal_invariant_lattice.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_tensor81_execution_lattice.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_universal_mutation_contract.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/hhs_universal_reversibility_adjudicator.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_python/runtime/runtime_object_registry.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_realtime_phase_certification_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_receipt_replay_verifier_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_regression_suite_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `hhs_runtime/HARMONICODE_VM_RUNTIME.c` | C runtime/bridge source candidate; must be reached through Makefile/ABI build or explicit kernel adapter | `True` |
| `hhs_runtime/acceleration/HHSAccelerationFabric.ts` | runtime subpackage candidate retained for guarded contract integration | `True` |
| … | 208 additional records omitted; see `RUNTIME_INTEGRATION_DECISIONS.json`. | … |


## DOCUMENTED_ONLY

These files carry state, reports, specifications, configuration, generated runtime evidence, or release context. They are not executable runtime pathways.

| Path | Reason | Guarded Entry Required |
|---|---|---|
| `.github/workflows/hhs-acceptance-gate.yml` | build/configuration/CI artifact; governed by release process rather than runtime dispatch | `False` |
| `CHANGELOG_PASS_002.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_003.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_004.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_005.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_006.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_007.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_008.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_009.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_010.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_011.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_012.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_013.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_014.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_015.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_016.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_017.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_018.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_019.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_020.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `CHANGELOG_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `DEVELOPMENT_OUTLINE.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `EXECUTION_GRAPH_PASS_021.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `EXECUTION_GRAPH_PASS_022.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `EXECUTION_GRAPH_PASS_023.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `GUARDED_PLUGIN_ADAPTERS_PASS_023.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `GUARDED_PLUGIN_ADAPTERS_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `HHS_FOUNDATIONAL_STANDARDS.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_002.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_003.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_004.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_005.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_006.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_007.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_008.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_009.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_010.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_011.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_012.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_014.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_015.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_016.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_017.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_018.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_019.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_020.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `INTEGRATION_REPORT_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_002.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_003.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_004.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_005.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_006.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_007.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_008.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_009.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_010.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_011.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_012.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_014.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_015.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_016.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_017.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_018.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_019.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_020.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `KNOWN_ISSUES_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `MODULE_REACHABILITY_REPORT_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `MODULE_REACHABILITY_REPORT_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `MODULE_REACHABILITY_REPORT_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `Makefile` | build/configuration/CI artifact; governed by release process rather than runtime dispatch | `False` |
| `NEXT_PASS_005.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_006.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_007.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_008.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_009.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_010.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_011.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_012.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_013.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_014.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_015.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_016.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_017.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_018.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_019.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_020.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `NEXT_PASS_024.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `ORPHAN_MODULES_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `ORPHAN_MODULES_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `ORPHAN_MODULES_PASS_023.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `PROJECT_STATE.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `RUNTIME_INTEGRATION_DECISIONS.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `RUNTIME_REACHABILITY_MANIFEST.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `SCHEMA_REQUIREMENTS.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_002.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_003.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_004.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_005.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_006.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_007.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_008.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_009.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_010.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_011.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_012.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_013.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_014.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_015.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_016.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_017.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_018.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| … | 56 additional records omitted; see `RUNTIME_INTEGRATION_DECISIONS.json`. | … |


## Kernel Witness

```json
{
  "canonical_payload": "\"{\\\"decision_count\\\": 557, \\\"decision_counts\\\": {\\\"DOCUMENTED_ONLY\\\": 176, \\\"PLUGIN_READY\\\": 368, \\\"WIRED\\\": 13}, \\\"schema\\\": \\\"HHS_RUNTIME_INTEGRATION_DECISIONS_V1\\\", \\\"version\\\": \\\"PASS_023\\\"}\"",
  "digest": "Pn?6hw+?0bvkqQAJ!m14KAuFFKom??IkVbsHPRL-ZU(HsF9jIZ3AA!/58F-v!qTIWUS6Q0*G",
  "dna": "Pn?6hw+?0bvkqQAJ!m14KAuFFKom??IkVbsHPRL-ZU(HsF9jIZ3AA!/58F-v!qTIWUS6Q0*G",
  "label": "hhs_runtime_integration_decisions_v1",
  "positions": [
    51,
    23,
    71,
    6,
    17,
    32,
    63,
    71,
    0,
    11,
    31,
    20,
    26,
    52,
    36,
    45,
    70,
    22,
    1,
    4,
    46,
    36,
    30,
    41,
    41,
    46,
    24,
    22,
    71,
    71,
    44,
    20,
    57,
    11,
    28,
    43,
    51,
    53,
    47,
    62,
    61,
    56,
    66,
    43,
    28,
    41,
    9,
    19,
    44,
    61,
    3,
    36,
    36,
    70,
    65,
    5,
    8,
    41,
    62,
    31,
    70,
    26,
    55,
    44,
    58,
    56,
    54,
    6,
    52,
    0,
    64,
    42
  ],
  "rotation_profile": [
    -21,
    22,
    69,
    -69,
    13,
    27,
    -15,
    64,
    -80,
    2,
    21,
    9,
    14,
    39,
    -50,
    30,
    -18,
    5,
    -89,
    -15,
    26,
    15,
    8,
    -54,
    17,
    21,
    -2,
    -5,
    43,
    -30,
    14,
    -11,
    -47,
    50,
    -6,
    -64,
    87,
    -56,
    9,
    -49,
    21,
    15,
    24,
    0,
    -16,
    68,
    -37,
    -28,
    -4,
    12,
    -47,
    57,
    -16,
    17,
    11,
    22,
    -120,
    56,
    4,
    -28,
    10,
    37,
    -7,
    -19,
    -6,
    -9,
    -12,
    11,
    56,
    -69,
    66,
    7
  ],
  "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
  "trace_count": 234,
  "zero_sum": true
}
```
