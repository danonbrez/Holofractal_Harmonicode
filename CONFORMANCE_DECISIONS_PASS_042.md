# Conformance Decisions — Pass 042

Decision count: `52`

| Surface | Decision | Complete |
|---|---|---|
| api_route:GET /api/runtime/conformance/invariants | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| api_route:GET /api/runtime/conformance/invariants/{invariant_id} | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| api_route:GET /api/runtime/conformance/status | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| api_route:GET /api/runtime/conformance/surfaces | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| api_route:GET /api/runtime/conformance/surfaces/{surface_id} | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| api_route:POST /api/runtime/conformance/evaluate | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| control_flow_gate:audited_if | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| control_flow_gate:audited_loop | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:authority_gate.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:authorized_execution_failure_policy.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:authorized_pure_function_executor.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:c_bridge.abi_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:closure_harness.bounded_runtime_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:constraint_stack_security_harness.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:contract_schema_registry.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:control_flow.transition_audit_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:controlled_live_plugin_executor.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:dryrun_live_plugin_executor.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:foundational_standards.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:genesis_severance_protocol.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:guarded_plugin_adapters.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:guarded_plugin_invocation_executor.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:hash72.kernel_authority_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:hhfs_carrier_adapter.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:hhfs_carrier_capsule.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:hhfs_reconstruction_protocol.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:io_gateway.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:kernel_conformance_decision.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:kernel_conformance_registration.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:kernel_conformance_surface_map.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:kernel_invariant_registry.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:ledger.verify | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:metadata_enhancement_block.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:persistence.guard_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:phase_disjoint_continuity.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:plugin_capability_planner.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:readonly_live_plugin_adapter.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:reality_to_manifold_translation.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:runtime_constraint_enforcement.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:runtime_contract.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:runtime_dataflow.guard_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:runtime_integration.decisions_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:runtime_reachability.audit_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:semantic_memory.guard_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:semantic_plugin_adapter_runtime.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:srcg.primitive_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:srcg.selfsolve_ab_gate | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:system_closure.harness_self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:transformation_permanence_validator.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:udfp_frame.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:validation_residue_compressor.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
| service:zero_bypass_runtime_interposer.self_test | ADMIT_MULTI_INVARIANT_DERIVATION | True |
