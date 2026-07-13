# Runtime Integration Decisions — Pass 022

## Purpose

Pass 022 converts silent orphan candidates into explicit release decisions. This is not deletion and not semantic rewriting. It is the first controlled reduction of the orphan frontier created in Pass 021.

## Decision Counts

```json
{
  "DOCUMENTED_ONLY": 165,
  "PLUGIN_READY": 379
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
| `harmonicode_modality_verbatim_ingestion_v1-1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
| `harmonicode_verbatim_semantic_database_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
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
| `hhs_database_integration_layer_v1.py` | legacy/high-value source retained for guarded adapter integration; no direct execution authorized | `True` |
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
| … | 219 additional records omitted; see `RUNTIME_INTEGRATION_DECISIONS.json`. | … |


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
| `DEVELOPMENT_OUTLINE.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `EXECUTION_GRAPH_PASS_021.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `EXECUTION_GRAPH_PASS_022.json` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
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
| `MODULE_REACHABILITY_REPORT_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `MODULE_REACHABILITY_REPORT_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
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
| `ORPHAN_MODULES_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `ORPHAN_MODULES_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
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
| `TEST_REPORT_PASS_019.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_020.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_021.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `TEST_REPORT_PASS_022.md` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `WordnetThesaurus.csv` | repository state/report/spec artifact; canonical context but not an executable entrypoint | `False` |
| `data/runtime/hhs_filesystem_ledger.json` | generated runtime state/data artifact; not an executable entrypoint | `False` |
| `data/runtime/hhs_unified_hash72_ledger.json` | generated runtime state/data artifact; not an executable entrypoint | `False` |
| `data/runtime/persistence_guard_self_test.json` | generated runtime state/data artifact; not an executable entrypoint | `False` |
| `data/runtime/persistence_guard_self_test.txt` | generated runtime state/data artifact; not an executable entrypoint | `False` |
| `gui/hhs-mobile-runtime-console/package.json` | build/configuration/CI artifact; governed by release process rather than runtime dispatch | `False` |
| … | 45 additional records omitted; see `RUNTIME_INTEGRATION_DECISIONS.json`. | … |


## Kernel Witness

```json
{
  "canonical_payload": "\"{\\\"decision_count\\\": 544, \\\"decision_counts\\\": {\\\"DOCUMENTED_ONLY\\\": 165, \\\"PLUGIN_READY\\\": 379}, \\\"schema\\\": \\\"HHS_RUNTIME_INTEGRATION_DECISIONS_V1\\\", \\\"version\\\": \\\"PASS_022\\\"}\"",
  "digest": ")2?zzZ2Avmf>qM-sPNu6ORmYHK)SVcBMqk0?UB)XUdCh/U2yv599X/U6)wFcu58Az-JCrX4b",
  "dna": ")2?zzZ2Avmf>qM-sPNu6ORmYHK)SVcBMqk0?UB)XUdCh/U2yv599X/U6)wFcu58Az-JCrX4b",
  "label": "hhs_runtime_integration_decisions_v1",
  "positions": [
    67,
    2,
    71,
    35,
    35,
    61,
    2,
    36,
    31,
    22,
    15,
    69,
    26,
    48,
    62,
    28,
    51,
    49,
    30,
    6,
    50,
    53,
    22,
    60,
    43,
    46,
    67,
    54,
    57,
    12,
    37,
    48,
    26,
    20,
    0,
    71,
    56,
    37,
    67,
    59,
    56,
    13,
    38,
    17,
    65,
    56,
    2,
    34,
    31,
    5,
    9,
    9,
    59,
    65,
    56,
    6,
    67,
    32,
    41,
    12,
    30,
    5,
    8,
    36,
    35,
    62,
    45,
    38,
    27,
    59,
    4,
    11
  ],
  "rotation_profile": [
    67,
    1,
    -3,
    -40,
    31,
    -16,
    -4,
    29,
    -49,
    13,
    5,
    -14,
    14,
    35,
    -24,
    13,
    -37,
    32,
    -60,
    59,
    -42,
    32,
    0,
    -35,
    19,
    21,
    -31,
    27,
    29,
    -17,
    7,
    17,
    -78,
    59,
    -34,
    -36,
    92,
    -72,
    29,
    -52,
    16,
    44,
    -4,
    -26,
    21,
    11,
    -44,
    -13,
    55,
    -44,
    -41,
    30,
    7,
    12,
    2,
    23,
    -61,
    -25,
    55,
    25,
    -30,
    16,
    18,
    45,
    -29,
    -75,
    -21,
    43,
    31,
    -10,
    6,
    -24
  ],
  "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
  "trace_count": 219,
  "zero_sum": true
}
```
