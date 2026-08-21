# HHS / HARMONICODE v1 release build surface
# Scope: C runtime ABI and standalone VM81 verification only.

CC ?= gcc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Ihhs_runtime/include -Ihhs_runtime/c
LDFLAGS ?= -lm
RUNTIME_BUILD_DIR := hhs_runtime/builds
ABI_LIB := $(RUNTIME_BUILD_DIR)/libhhs_runtime.so
VM81_BIN := $(RUNTIME_BUILD_DIR)/hhs_vm81

.PHONY: all c-kernel c-abi vm81 verify-c emulate-c service-registry io-gateway semantic-memory-guard runtime-dataflow-guard persistence-guard runtime-contract foundational-standards hash72-u72 hash72-kernel-authority backend-routes gui-runtime-contract srcg-primitive srcg-api-surface system-closure-harness runtime-reachability runtime-integration-decisions guarded-plugin-adapters plugin-capability-planner guarded-plugin-invocation-executor contract-schema-registry constraint-stack-security-harness runtime-constraint-enforcement zero-bypass-runtime-interposer test clean

all: c-kernel

c-kernel: c-abi vm81

$(RUNTIME_BUILD_DIR):
	mkdir -p $(RUNTIME_BUILD_DIR)

c-abi: $(ABI_LIB)

$(ABI_LIB): hhs_runtime/c/hhs_runtime_abi.c hhs_runtime/src/hhs_hash216.c hhs_runtime/c/hhs_runtime_abi.h hhs_runtime/include/hhs_hash216.h | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) -fPIC -shared hhs_runtime/c/hhs_runtime_abi.c hhs_runtime/src/hhs_hash216.c -o $(ABI_LIB) $(LDFLAGS)

vm81: $(VM81_BIN)

$(VM81_BIN): hhs_runtime/HARMONICODE_VM_RUNTIME.c hhs_runtime/include/HARMONICODE_VM_RUNTIME.h | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) hhs_runtime/HARMONICODE_VM_RUNTIME.c -o $(VM81_BIN) $(LDFLAGS)

verify-c: c-kernel
	$(VM81_BIN) --verify
	test -f $(ABI_LIB)
	nm -D $(ABI_LIB) | grep -E 'hhs_runtime_init|hhs_runtime_step|hhs_validate_abi|hhs_hash216_compute'

emulate-c: c-kernel
	python -m hhs_python.runtime.hhs_runtime_emulator

service-registry: c-kernel
	python -m hhs_runtime.hhs_service_registry_v1

io-gateway: c-kernel
	python -m hhs_runtime.hhs_io_gateway_v1

semantic-memory-guard: c-kernel
	python -m hhs_runtime.hhs_semantic_memory_guard_v1

runtime-dataflow-guard: c-kernel
	python -m hhs_runtime.hhs_runtime_dataflow_guard_v1

persistence-guard: c-kernel
	python -m hhs_runtime.hhs_persistence_guard_v1

runtime-contract: c-kernel
	python -m hhs_runtime.hhs_runtime_contract_v1

foundational-standards: c-kernel
	python -m hhs_foundation.hhs_foundational_standards_v1

hash72-u72: c-kernel
	pytest -q tests/test_hhs_hash72_u72_ring_v1.py

hash72-kernel-authority: c-kernel
	pytest -q tests/test_hhs_hash72_kernel_authority_v1.py

backend-routes: c-kernel
	pytest -q tests/test_hhs_backend_guarded_routes_v1.py

test: c-kernel
	pytest -q

clean:
	rm -rf $(RUNTIME_BUILD_DIR)

.PHONY: hash72-kernel-surfaces
hash72-kernel-surfaces:
	python -m pytest -q tests/test_hhs_hash72_kernel_surface_unification_v1.py


gui-runtime-contract:
	python -m pytest -q tests/test_hhs_gui_runtime_contract_surface_v1.py


srcg-primitive: c-kernel
	python -m pytest -q tests/test_hhs_srcg_gate_v1.py


srcg-api-surface: c-kernel
	python -m pytest -q tests/test_hhs_backend_guarded_routes_v1.py tests/test_hhs_gui_runtime_contract_surface_v1.py


system-closure-harness: c-kernel
	python -m pytest -q tests/test_hhs_system_closure_harness_v1.py


runtime-reachability: c-kernel
	python -m hhs_runtime.hhs_runtime_reachability_audit_v1


runtime-integration-decisions: c-kernel
	python -m hhs_runtime.hhs_runtime_integration_decisions_v1


guarded-plugin-adapters: c-kernel
	python -m hhs_runtime.hhs_guarded_plugin_adapters_v1

plugin-capability-planner: c-kernel
	python -m hhs_runtime.hhs_plugin_capability_planner_v1



guarded-plugin-invocation-executor: c-kernel
	python -m hhs_runtime.hhs_guarded_plugin_invocation_executor_v1

semantic-plugin-adapter-runtime: c-kernel
	python -m hhs_runtime.hhs_semantic_plugin_adapter_runtime_v1


controlled-live-plugin-executor: c-kernel
	python -m hhs_runtime.hhs_controlled_live_plugin_executor_v1


readonly-live-plugin-adapter: c-kernel
	python -m hhs_runtime.hhs_readonly_live_plugin_adapter_v1


dryrun-live-plugin-executor: c-kernel
	python -m hhs_runtime.hhs_dryrun_live_plugin_executor_v1


contract-schema-registry: c-kernel
	python -m hhs_runtime.hhs_contract_schema_registry_v1


authorized-pure-function-executor: c-kernel
	python -m hhs_runtime.hhs_authorized_pure_function_executor_v1

authorized-execution-failure-policy: c-kernel
	python -m hhs_runtime.hhs_authorized_execution_failure_policy_v1

.PHONY: constraint-stack-security-harness
constraint-stack-security-harness: c-kernel
	python -m hhs_runtime.hhs_constraint_stack_security_harness_v1

.PHONY: reality-to-manifold-translation
reality-to-manifold-translation: c-kernel
	python -m hhs_runtime.hhs_reality_to_manifold_translation_v1

.PHONY: runtime-constraint-enforcement
runtime-constraint-enforcement: c-kernel
	python -m hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1

.PHONY: zero-bypass-runtime-interposer
zero-bypass-runtime-interposer: c-kernel
	python -m hhs_runtime.hhs_zero_bypass_runtime_interposer_v1

.PHONY: phase-disjoint-continuity
phase-disjoint-continuity: c-kernel
	python -m hhs_runtime.hhs_phase_disjoint_continuity_v1

.PHONY: genesis-severance-protocol
genesis-severance-protocol: c-kernel
	python -m hhs_runtime.hhs_genesis_severance_protocol_v1

.PHONY: transformation-permanence-validator
transformation-permanence-validator: c-kernel
	python -m hhs_runtime.hhs_transformation_permanence_validator_v1

.PHONY: phase-disjoint-continuity-tests
phase-disjoint-continuity-tests: c-kernel
	python -m pytest -q tests/test_hhs_phase_disjoint_continuity_v1.py tests/test_hhs_genesis_severance_protocol_v1.py tests/test_hhs_transformation_permanence_validator_v1.py

.PHONY: hhfs-carrier-capsule
hhfs-carrier-capsule: c-kernel
	python -m hhs_runtime.hhs_hhfs_carrier_capsule_v1

.PHONY: metadata-enhancement-block
metadata-enhancement-block: c-kernel
	python -m hhs_runtime.hhs_metadata_enhancement_block_v1

.PHONY: udfp-frame
udfp-frame: c-kernel
	python -m hhs_runtime.hhs_udfp_frame_v1

.PHONY: hhfs-udfp-tests
hhfs-udfp-tests: c-kernel
	python -m pytest -q tests/test_hhs_hhfs_carrier_capsule_v1.py tests/test_hhs_metadata_enhancement_block_v1.py tests/test_hhs_udfp_frame_v1.py

.PHONY: validation-residue-compressor
validation-residue-compressor: c-kernel
	python -m hhs_runtime.hhs_validation_residue_compressor_v1

.PHONY: hhfs-carrier-adapter
hhfs-carrier-adapter: c-kernel
	python -m hhs_runtime.hhs_hhfs_carrier_adapter_v1

.PHONY: hhfs-reconstruction-protocol
hhfs-reconstruction-protocol: c-kernel
	python -m hhs_runtime.hhs_hhfs_reconstruction_protocol_v1

.PHONY: hhfs-carrier-reconstruction-tests
hhfs-carrier-reconstruction-tests: c-kernel
	python -m pytest -q tests/test_hhs_validation_residue_compressor_v1.py tests/test_hhs_hhfs_carrier_adapter_v1.py tests/test_hhs_hhfs_reconstruction_protocol_v1.py


.PHONY: closure-harness-bounded-runtime
closure-harness-bounded-runtime: c-kernel
	python -m hhs_runtime.hhs_closure_harness_bounded_runtime_v1

.PHONY: control-flow-transition-audit
control-flow-transition-audit: c-kernel
	python -m hhs_runtime.hhs_control_flow_transition_audit_v1

.PHONY: closure-control-flow-tests
closure-control-flow-tests: c-kernel
	python -m pytest -q tests/test_hhs_closure_harness_bounded_runtime_v1.py tests/test_hhs_control_flow_transition_audit_v1.py tests/test_hhs_control_flow_gates_pass041_v1.py tests/test_hhs_system_closure_harness_v1.py

.PHONY: kernel-invariant-registry
kernel-invariant-registry: c-kernel
	python -m hhs_runtime.hhs_kernel_invariant_registry_v1

.PHONY: kernel-conformance-surface-map
kernel-conformance-surface-map: c-kernel
	python -m hhs_runtime.hhs_kernel_conformance_surface_map_v1

.PHONY: kernel-conformance-decision
kernel-conformance-decision: c-kernel
	python -m hhs_runtime.hhs_kernel_conformance_decision_v1

.PHONY: kernel-conformance-tests
kernel-conformance-tests: c-kernel
	python -m pytest -q tests/test_hhs_kernel_invariant_registry_v1.py tests/test_hhs_kernel_conformance_surface_map_v1.py tests/test_hhs_kernel_conformance_decision_v1.py tests/test_hhs_kernel_conformance_registration_interposer_v1.py tests/test_hhs_service_registry_kernel_derivation_pass042_v1.py tests/test_hhs_runtime_reachability_kernel_derivation_pass042_v1.py tests/test_hhs_control_flow_kernel_derivation_pass042_v1.py tests/test_hhs_constraint_enforcement_kernel_derivation_pass042_v1.py tests/test_hhs_contract_schema_kernel_ownership_pass042_v1.py tests/test_hhs_closure_harness_conformance_map_pass042_v1.py

.PHONY: kernel-conformance-full
kernel-conformance-full: kernel-invariant-registry kernel-conformance-surface-map kernel-conformance-tests runtime-reachability system-closure-harness

.PHONY: kernel-runtime-autocomposer
kernel-runtime-autocomposer: c-kernel
	python -m hhs_runtime.hhs_kernel_runtime_autocomposer_v1

.PHONY: validation-residue-compactor-pass043
validation-residue-compactor-pass043: c-kernel
	python -m hhs_runtime.hhs_validation_residue_compactor_v1

.PHONY: bounded-metadata-lifecycle
bounded-metadata-lifecycle: c-kernel
	python -m hhs_runtime.hhs_bounded_metadata_lifecycle_v1

.PHONY: expanded-state-decay-lifecycle
expanded-state-decay-lifecycle: c-kernel
	python -m hhs_runtime.hhs_expanded_state_decay_lifecycle_v1

.PHONY: kernel-autocomposition-tests
kernel-autocomposition-tests: c-kernel
	python -m pytest -q tests/test_hhs_kernel_runtime_autocomposer_v1.py tests/test_hhs_validation_residue_compactor_v1.py tests/test_hhs_bounded_metadata_lifecycle_v1.py tests/test_hhs_conformance_decision_cache_v1.py tests/test_hhs_runtime_composition_performance_profile_v1.py tests/test_hhs_expanded_state_decay_lifecycle_v1.py

.PHONY: kernel-autocomposition-full
kernel-autocomposition-full: kernel-runtime-autocomposer validation-residue-compactor-pass043 bounded-metadata-lifecycle expanded-state-decay-lifecycle kernel-autocomposition-tests kernel-conformance-full runtime-reachability system-closure-harness

.PHONY: semantic-composition-cache
semantic-composition-cache: c-kernel
	python -m hhs_runtime.hhs_semantic_composition_cache_v1

.PHONY: composition-dependency-index
composition-dependency-index: c-kernel
	python -m hhs_runtime.hhs_composition_dependency_index_v1

.PHONY: composition-cache-invalidation
composition-cache-invalidation: c-kernel
	python -m hhs_runtime.hhs_composition_cache_invalidation_v1

.PHONY: incremental-pipeline-rebuilder
incremental-pipeline-rebuilder: c-kernel
	python -m hhs_runtime.hhs_incremental_pipeline_rebuilder_v1

.PHONY: semantic-runtime-query
semantic-runtime-query: c-kernel
	python -m hhs_runtime.hhs_semantic_runtime_query_v1

.PHONY: semantic-composition-cache-tests
semantic-composition-cache-tests: c-kernel
	python -m pytest -q tests/test_hhs_semantic_composition_cache_v1.py tests/test_hhs_composition_dependency_index_v1.py tests/test_hhs_composition_cache_invalidation_v1.py tests/test_hhs_incremental_pipeline_rebuilder_v1.py tests/test_hhs_semantic_runtime_query_v1.py

.PHONY: semantic-composition-cache-full
semantic-composition-cache-full: semantic-composition-cache composition-dependency-index composition-cache-invalidation incremental-pipeline-rebuilder semantic-runtime-query semantic-composition-cache-tests kernel-autocomposition-full runtime-reachability system-closure-harness

.PHONY: live-fastapi-runtime
live-fastapi-runtime: c-kernel
	python -m hhs_backend.server

.PHONY: live-kernel-event-bridge
live-kernel-event-bridge: c-kernel
	python -m hhs_backend.runtime.live_kernel_event_bridge_v1

.PHONY: websocket-kernel-channel-router
websocket-kernel-channel-router: c-kernel
	python -m hhs_backend.runtime.websocket_kernel_channel_router_v1

.PHONY: node-proxy-contract
node-proxy-contract:
	python -m hhs_backend.runtime.node_proxy_contract_v1

.PHONY: live-runtime-smoke
live-runtime-smoke: c-kernel
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_live_fastapi_runtime_pass045_v1.py tests/test_hhs_websocket_kernel_channel_binding_pass045_v1.py tests/test_hhs_node_proxy_contract_pass045_v1.py

.PHONY: live-fastapi-kernel-full
live-fastapi-kernel-full: live-kernel-event-bridge websocket-kernel-channel-router node-proxy-contract live-runtime-smoke

.PHONY: live-gui-projection-contract
live-gui-projection-contract: c-kernel
	python -m hhs_backend.runtime.gui_projection_contract_v1

.PHONY: live-gui-websocket-binding
live-gui-websocket-binding: c-kernel
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_live_gui_websocket_binding_pass046_v1.py

.PHONY: live-gui-full
live-gui-full: live-fastapi-kernel-full live-gui-projection-contract live-gui-websocket-binding live-gui-browser-e2e-source runtime-reachability

.PHONY: live-gui-browser-e2e-source
live-gui-browser-e2e-source:
	cd hhs_gui && node ./scripts/live-gui-e2e-source-verify.mjs

.PHONY: live-gui-browser-e2e
live-gui-browser-e2e: live-gui-browser-e2e-source
	@echo "Playwright spec available at tests/e2e/live_gui_websocket_binding.spec.ts"

.PHONY: live-gui-command-contract
live-gui-command-contract: c-kernel
	python -m hhs_backend.runtime.live_gui_command_contract_v1

.PHONY: live-gui-command-router
live-gui-command-router: c-kernel
	python -m hhs_backend.runtime.live_gui_command_router_v1

.PHONY: live-gui-command-authority-loop
live-gui-command-authority-loop: c-kernel
	python -m hhs_backend.runtime.live_gui_command_authority_loop_v1

.PHONY: live-gui-command-authority
live-gui-command-authority: c-kernel
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_live_gui_command_authority_pass047_v1.py

.PHONY: live-gui-command-full
live-gui-command-full: live-gui-full live-gui-command-contract live-gui-command-router live-gui-command-authority-loop live-gui-command-authority live-gui-browser-e2e-source runtime-reachability

.PHONY: live-authorized-mutation-contract live-state-reversal-witness live-mutation-receipt-chain live-authorized-mutation-executor live-authorized-mutation live-gui-authorized-mutation-full

live-authorized-mutation-contract:
	python -m hhs_backend.runtime.live_authorized_mutation_contract_v1

live-state-reversal-witness:
	python -m hhs_backend.runtime.live_state_reversal_witness_v1

live-mutation-receipt-chain:
	python -m hhs_backend.runtime.live_mutation_receipt_chain_v1

live-authorized-mutation-executor:
	python -m hhs_backend.runtime.live_authorized_mutation_executor_v1

live-authorized-mutation:
	python -m pytest -q tests/test_hhs_live_authorized_mutation_pass048_v1.py

live-gui-authorized-mutation-full:
	$(MAKE) live-gui-command-authority
	$(MAKE) live-authorized-mutation-contract
	$(MAKE) live-state-reversal-witness
	$(MAKE) live-mutation-receipt-chain
	$(MAKE) live-authorized-mutation-executor
	$(MAKE) live-authorized-mutation
	$(MAKE) live-gui-browser-e2e-source
	$(MAKE) runtime-reachability

.PHONY: visual-runtime-workspace workspace-object-model workspace-multimodal-ingress workspace-symbolic-document workspace-interpreter workspace-compiler-ir workspace-compiler workspace-emulator workspace-graph-projection workspace-semantic-memory workspace-persistence workspace-command-router workspace-authority-loop workspace-gui-source workspace-tests visual-runtime-workspace-full

visual-runtime-workspace:
	python -m hhs_backend.runtime.runtime_workspace_project_v1

workspace-object-model:
	python -m hhs_backend.runtime.runtime_workspace_object_v1

workspace-multimodal-ingress:
	python -m hhs_backend.runtime.multimodal_workspace_ingress_v1

workspace-symbolic-document:
	python -m hhs_backend.runtime.hhs_symbolic_document_service_v1

workspace-interpreter:
	python -m hhs_backend.runtime.hhs_live_interpreter_v1

workspace-compiler-ir:
	python -m hhs_backend.runtime.hhs_compiler_ir_v1

workspace-compiler:
	python -m hhs_backend.runtime.hhs_interpreting_compiler_v1

workspace-emulator:
	python -m hhs_backend.runtime.hhs_visual_emulator_session_v1

workspace-graph-projection:
	python -m hhs_backend.runtime.hhs_workspace_graph_projection_v1

workspace-semantic-memory:
	python -m hhs_backend.runtime.hhs_workspace_semantic_memory_v1

workspace-persistence:
	python -m hhs_backend.runtime.hhs_workspace_persistence_v1

workspace-command-router:
	python -m hhs_backend.runtime.hhs_workspace_command_router_v1

workspace-authority-loop:
	python -m hhs_backend.runtime.hhs_workspace_authority_loop_v1

workspace-gui-source:
	cd hhs_gui && node ./scripts/workspace-source-verify.mjs

workspace-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
		tests/test_hhs_runtime_workspace_project_v1.py \
		tests/test_hhs_runtime_workspace_object_v1.py \
		tests/test_hhs_multimodal_workspace_ingress_v1.py \
		tests/test_hhs_symbolic_document_service_v1.py \
		tests/test_hhs_live_interpreter_v1.py \
		tests/test_hhs_interpreting_compiler_v1.py \
		tests/test_hhs_visual_emulator_session_v1.py \
		tests/test_hhs_workspace_graph_projection_v1.py \
		tests/test_hhs_workspace_semantic_memory_v1.py \
		tests/test_hhs_workspace_persistence_v1.py \
		tests/test_hhs_workspace_authority_loop_v1.py \
		tests/test_hhs_visual_runtime_workspace_gui_pass049_v1.py \
		tests/test_hhs_workspace_command_boundary_pass049_v1.py \
		tests/test_hhs_workspace_multimodal_ingress_gui_pass049_v1.py \
		tests/test_hhs_workspace_interpret_compile_emulate_gui_pass049_v1.py

visual-runtime-workspace-full:
	$(MAKE) verify-c
	$(MAKE) workspace-object-model
	$(MAKE) workspace-multimodal-ingress
	$(MAKE) workspace-symbolic-document
	$(MAKE) workspace-interpreter
	$(MAKE) workspace-compiler-ir
	$(MAKE) workspace-compiler
	$(MAKE) workspace-emulator
	$(MAKE) workspace-graph-projection
	$(MAKE) workspace-semantic-memory
	$(MAKE) workspace-persistence
	$(MAKE) workspace-command-router
	$(MAKE) workspace-authority-loop
	$(MAKE) workspace-gui-source
	$(MAKE) workspace-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) system-closure-harness

.PHONY: modality-source-commitment universal-modality-adapter modality-projection-registry cross-modal-transformation-plan derived-artifact-pipeline artifact-lineage-registry modality-reconstruction-recipe modality-adapter-capability-map universal-artifact-pipeline universal-modality-pipeline-tests universal-modality-pipeline-full

modality-source-commitment:
	python -m hhs_backend.runtime.hhs_modality_source_commitment_v1

universal-modality-adapter:
	python -m hhs_backend.runtime.hhs_universal_modality_adapter_v1

modality-projection-registry:
	python -m hhs_backend.runtime.hhs_modality_projection_registry_v1

cross-modal-transformation-plan:
	python -m hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1

derived-artifact-pipeline:
	python -m hhs_backend.runtime.hhs_derived_artifact_pipeline_v1

artifact-lineage-registry:
	python -m hhs_backend.runtime.hhs_artifact_lineage_registry_v1

modality-reconstruction-recipe:
	python -m hhs_backend.runtime.hhs_modality_reconstruction_recipe_v1

modality-adapter-capability-map:
	python -m hhs_backend.runtime.hhs_modality_adapter_capability_map_v1

universal-artifact-pipeline:
	python -m hhs_backend.runtime.hhs_universal_artifact_pipeline_v1

universal-modality-pipeline-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
		tests/test_hhs_universal_modality_adapter_pass050_v1.py \
		tests/test_hhs_universal_artifact_pipeline_pass050_v1.py \
		tests/test_hhs_multimodal_workspace_ingress_v1.py

universal-modality-pipeline-full:
	$(MAKE) verify-c
	$(MAKE) modality-source-commitment
	$(MAKE) universal-modality-adapter
	$(MAKE) modality-projection-registry
	$(MAKE) cross-modal-transformation-plan
	$(MAKE) derived-artifact-pipeline
	$(MAKE) artifact-lineage-registry
	$(MAKE) modality-reconstruction-recipe
	$(MAKE) modality-adapter-capability-map
	$(MAKE) universal-artifact-pipeline
	$(MAKE) universal-modality-pipeline-tests
	$(MAKE) workspace-gui-source
	$(MAKE) service-registry
	$(MAKE) runtime-reachability

.PHONY: runtime-canonical-observer capability-contract capability-provider-registry capability-resolution provider-execution-proposal capability-policy-gate provider-invocation-receipt provider-result-ingress capability-fallback-plan universal-capability-fabric universal-capability-fabric-tests universal-capability-fabric-full

runtime-canonical-observer:
	python -m hhs_backend.runtime.hhs_runtime_canonical_observer_v1

capability-contract:
	python -m hhs_backend.runtime.hhs_capability_contract_v1

capability-provider-registry:
	python -m hhs_backend.runtime.hhs_capability_provider_registry_v1

capability-resolution:
	python -m hhs_backend.runtime.hhs_capability_resolution_v1

provider-execution-proposal:
	python -m hhs_backend.runtime.hhs_provider_execution_proposal_v1

capability-policy-gate:
	python -m hhs_backend.runtime.hhs_capability_policy_gate_v1

provider-invocation-receipt:
	python -m hhs_backend.runtime.hhs_provider_invocation_receipt_v1

provider-result-ingress:
	python -m hhs_backend.runtime.hhs_provider_result_ingress_v1

capability-fallback-plan:
	python -m hhs_backend.runtime.hhs_capability_fallback_plan_v1

universal-capability-fabric:
	python -m hhs_backend.runtime.hhs_universal_capability_fabric_v1

universal-capability-fabric-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
		tests/test_hhs_runtime_canonical_observer_pass051_v1.py \
		tests/test_hhs_universal_capability_fabric_pass051_v1.py \
		tests/test_hhs_capability_gui_source_pass051_v1.py

universal-capability-fabric-full:
	$(MAKE) verify-c
	$(MAKE) runtime-canonical-observer
	$(MAKE) capability-contract
	$(MAKE) capability-provider-registry
	$(MAKE) capability-resolution
	$(MAKE) provider-execution-proposal
	$(MAKE) capability-policy-gate
	$(MAKE) provider-invocation-receipt
	$(MAKE) provider-result-ingress
	$(MAKE) capability-fallback-plan
	$(MAKE) universal-capability-fabric
	$(MAKE) universal-capability-fabric-tests
	$(MAKE) workspace-gui-source
	$(MAKE) service-registry
	$(MAKE) runtime-reachability

.PHONY: document-provider-contract pdf-native-text-provider pdf-page-geometry-provider document-image-region-provider ocr-provider document-structure-fusion document-projection-bundle document-perception-receipt document-reconstruction-plan deep-document-perception-pipeline deep-document-perception-tests deep-document-perception-full

document-provider-contract:
	python -m hhs_backend.runtime.hhs_document_provider_contract_v1

pdf-native-text-provider:
	python -m hhs_backend.runtime.hhs_pdf_native_text_provider_v1

pdf-page-geometry-provider:
	python -m hhs_backend.runtime.hhs_pdf_page_geometry_provider_v1

document-image-region-provider:
	python -m hhs_backend.runtime.hhs_document_image_region_provider_v1

ocr-provider:
	python -m hhs_backend.runtime.hhs_ocr_provider_v1

document-structure-fusion:
	python -m hhs_backend.runtime.hhs_document_structure_fusion_v1

document-projection-bundle:
	python -m hhs_backend.runtime.hhs_document_projection_bundle_v1

document-perception-receipt:
	python -m hhs_backend.runtime.hhs_document_perception_receipt_v1

document-reconstruction-plan:
	python -m hhs_backend.runtime.hhs_document_reconstruction_plan_v1

deep-document-perception-pipeline:
	python -m hhs_backend.runtime.hhs_deep_document_perception_pipeline_v1

deep-document-perception-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
		tests/test_hhs_document_provider_contract_pass052_v1.py \
		tests/test_hhs_deep_document_perception_pipeline_pass052_v1.py \
		tests/test_hhs_document_perception_gui_source_pass052_v1.py

deep-document-perception-full:
	$(MAKE) verify-c
	$(MAKE) document-provider-contract
	$(MAKE) pdf-native-text-provider
	$(MAKE) pdf-page-geometry-provider
	$(MAKE) document-image-region-provider
	$(MAKE) ocr-provider
	$(MAKE) document-structure-fusion
	$(MAKE) document-projection-bundle
	$(MAKE) document-perception-receipt
	$(MAKE) document-reconstruction-plan
	$(MAKE) deep-document-perception-pipeline
	$(MAKE) deep-document-perception-tests
	$(MAKE) workspace-gui-source
	$(MAKE) service-registry
	$(MAKE) runtime-reachability

.PHONY: canonical-report-pass052-1 canonical-report-pass052-1-tests
canonical-report-pass052-1:
	python -m hhs_runtime.hhs_canonical_repository_report_v1
canonical-report-pass052-1-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_canonical_repository_report_pass052_1_v1.py

.PHONY: deep-audio-perception-pass053 deep-audio-perception-pass053-tests
deep-audio-perception-pass053:
	python -m hhs_backend.runtime.hhs_deep_audio_perception_pipeline_v1
deep-audio-perception-pass053-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_deep_audio_perception_pipeline_pass053_v1.py

.PHONY: canonical-authority-graph-pass054 authority-pass054-tests authority-pass054-full
canonical-authority-graph-pass054:
	python -m hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1

authority-pass054-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_canonical_authority_graph_pass054_v1.py tests/test_hhs_authority_response_gate_pass054_v1.py tests/test_hhs_cross_role_handoff_pass054_v1.py tests/test_hhs_authority_gui_source_pass054_v1.py

authority-pass054-full:
	$(MAKE) verify-c
	$(MAKE) canonical-authority-graph-pass054
	$(MAKE) authority-pass054-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map


.PHONY: authority-dispatch-pass055 authority-dispatch-pass055-tests authority-dispatch-pass055-full
authority-dispatch-pass055:
	python -m hhs_backend.runtime.hhs_authority_enforced_dispatch_v1

authority-dispatch-pass055-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_authority_enforced_dispatch_pass055_v1.py tests/test_hhs_capability_lease_pass055_v1.py tests/test_hhs_authority_dispatch_gui_source_pass055_v1.py

authority-dispatch-pass055-full:
	$(MAKE) verify-c
	$(MAKE) authority-dispatch-pass055
	$(MAKE) authority-dispatch-pass055-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: distributed-authority-federation-pass056 distributed-authority-federation-pass056-tests distributed-authority-federation-pass056-full
distributed-authority-federation-pass056:
	python -m hhs_backend.runtime.hhs_distributed_authority_federation_v1

distributed-authority-federation-pass056-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_distributed_authority_federation_pass056_v1.py tests/test_hhs_federation_gui_source_pass056_v1.py

distributed-authority-federation-pass056-full:
	$(MAKE) verify-c
	$(MAKE) distributed-authority-federation-pass056
	$(MAKE) distributed-authority-federation-pass056-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: partition-tolerant-federated-recovery-pass057 partition-tolerant-federated-recovery-pass057-tests partition-tolerant-federated-recovery-pass057-full
partition-tolerant-federated-recovery-pass057:
	python -m hhs_backend.runtime.hhs_partition_tolerant_federated_recovery_v1

partition-tolerant-federated-recovery-pass057-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_partition_tolerant_federated_recovery_pass057_v1.py tests/test_hhs_partition_recovery_gui_source_pass057_v1.py

partition-tolerant-federated-recovery-pass057-full:
	$(MAKE) verify-c
	$(MAKE) partition-tolerant-federated-recovery-pass057
	$(MAKE) partition-tolerant-federated-recovery-pass057-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: canonical-federated-state-reconciliation-pass058 canonical-federated-state-reconciliation-pass058-tests canonical-federated-state-reconciliation-pass058-full
canonical-federated-state-reconciliation-pass058:
	python -m hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1

canonical-federated-state-reconciliation-pass058-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_canonical_federated_state_reconciliation_pass058_v1.py tests/test_hhs_federated_reconciliation_gui_source_pass058_v1.py

canonical-federated-state-reconciliation-pass058-full:
	$(MAKE) verify-c
	$(MAKE) canonical-federated-state-reconciliation-pass058
	$(MAKE) canonical-federated-state-reconciliation-pass058-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map


.PHONY: canonical-federated-transaction-pass059 canonical-federated-transaction-pass059-tests canonical-federated-transaction-pass059-full
canonical-federated-transaction-pass059:
	python -m hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1

canonical-federated-transaction-pass059-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_canonical_federated_transaction_pass059_v1.py tests/test_hhs_federated_transaction_gui_source_pass059_v1.py

canonical-federated-transaction-pass059-full:
	$(MAKE) verify-c
	$(MAKE) canonical-federated-transaction-pass059
	$(MAKE) canonical-federated-transaction-pass059-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: federated-transaction-recovery-pass060 federated-transaction-recovery-pass060-tests federated-transaction-recovery-pass060-full
federated-transaction-recovery-pass060:
	python -m hhs_backend.runtime.hhs_federated_transaction_recovery_v1

federated-transaction-recovery-pass060-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_federated_transaction_recovery_pass060_v1.py tests/test_hhs_transaction_recovery_gui_source_pass060_v1.py

federated-transaction-recovery-pass060-full:
	$(MAKE) verify-c
	$(MAKE) federated-transaction-recovery-pass060
	$(MAKE) federated-transaction-recovery-pass060-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map


.PHONY: bounded-rejection-authority-pass061 bounded-rejection-authority-pass061-tests bounded-rejection-authority-pass061-full
bounded-rejection-authority-pass061:
	python -m hhs_backend.runtime.hhs_bounded_rejection_authority_v1

bounded-rejection-authority-pass061-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_bounded_rejection_authority_pass061_v1.py tests/test_hhs_bounded_rejection_gui_source_pass061_v1.py

bounded-rejection-authority-pass061-full:
	$(MAKE) verify-c
	$(MAKE) bounded-rejection-authority-pass061
	$(MAKE) bounded-rejection-authority-pass061-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map


.PHONY: global-reciprocal-contract-topology-pass062 global-reciprocal-contract-topology-pass062-tests global-reciprocal-contract-topology-pass062-full
global-reciprocal-contract-topology-pass062:
	python -m hhs_backend.runtime.hhs_global_reciprocal_contract_topology_v1

global-reciprocal-contract-topology-pass062-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_global_reciprocal_contract_topology_pass062_v1.py tests/test_hhs_global_reciprocal_topology_gui_source_pass062_v1.py

global-reciprocal-contract-topology-pass062-full:
	$(MAKE) verify-c
	$(MAKE) global-reciprocal-contract-topology-pass062
	$(MAKE) global-reciprocal-contract-topology-pass062-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: deterministic-manifold-execution-pass063 deterministic-manifold-execution-pass063-tests deterministic-manifold-execution-pass063-full
deterministic-manifold-execution-pass063:
	python -m hhs_backend.runtime.hhs_deterministic_manifold_execution_v1

deterministic-manifold-execution-pass063-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_deterministic_manifold_execution_pass063_v1.py tests/test_hhs_global_reciprocal_contract_topology_pass062_v1.py tests/test_hhs_bounded_rejection_authority_pass061_v1.py

deterministic-manifold-execution-pass063-full:
	$(MAKE) verify-c
	$(MAKE) deterministic-manifold-execution-pass063
	$(MAKE) deterministic-manifold-execution-pass063-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: dynamic-lo-shu-agent-tensor-pass067 dynamic-lo-shu-agent-tensor-pass067-tests dynamic-lo-shu-agent-tensor-pass067-full
dynamic-lo-shu-agent-tensor-pass067:
	python -m hhs_backend.runtime.hhs_dynamic_lo_shu_agent_tensor_v1

dynamic-lo-shu-agent-tensor-pass067-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_dynamic_lo_shu_agent_tensor_pass067_v1.py tests/test_hhs_agent_economy_pass066_v1.py

dynamic-lo-shu-agent-tensor-pass067-full:
	$(MAKE) verify-c
	$(MAKE) dynamic-lo-shu-agent-tensor-pass067
	$(MAKE) dynamic-lo-shu-agent-tensor-pass067-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: vm81-native-exposure-pass078 vm81-native-exposure-pass078-tests vm81-native-exposure-pass078-full
vm81-native-exposure-pass078:
	python -m native_projects.hhs_vm81_native_exposure.build_pass078_release

vm81-native-exposure-pass078-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass078_vm81_native_exposure_v1.py

vm81-native-exposure-pass078-full:
	$(MAKE) vm81-native-exposure-pass078
	$(MAKE) vm81-native-exposure-pass078-tests

.PHONY: pass-safe-resume-exit-pass112 pass-safe-resume-exit-pass112-tests pass-safe-resume-exit-pass112-full
pass-safe-resume-exit-pass112:
	python -m hhs_runtime.hhs_pass112_pass_safe_resume_exit_v1

pass-safe-resume-exit-pass112-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass111_predictive_continuation_cache_v1.py tests/test_hhs_pass112_pass_safe_resume_exit_v1.py

pass-safe-resume-exit-pass112-full:
	$(MAKE) pass-safe-resume-exit-pass112-tests
	$(MAKE) service-registry
	$(MAKE) runtime-reachability
	$(MAKE) kernel-conformance-surface-map

.PHONY: pass113-safe-lossless-archive
pass113-safe-lossless-archive:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass112_pass_safe_resume_exit_v1.py tests/test_hhs_pass113_safe_lossless_archive_v1.py

.PHONY: pass122-read-only-self-analysis pass122-read-only-self-analysis-tests
pass122-read-only-self-analysis:
	python -m hhs_runtime.hhs_pass122_read_only_self_analysis_v1

pass122-read-only-self-analysis-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass122_read_only_self_analysis_v1.py

.PHONY: pass123-bounded-token-generalization pass123-bounded-token-generalization-tests
pass123-bounded-token-generalization:
	python -m hhs_runtime.hhs_pass123_bounded_token_generalization_v1

pass123-bounded-token-generalization-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass123_bounded_token_generalization_v1.py

.PHONY: pass124-parallel-deterministic-generalization pass124-parallel-deterministic-generalization-tests
pass124-parallel-deterministic-generalization:
	python -m hhs_runtime.hhs_pass124_parallel_deterministic_generalization_v1

pass124-parallel-deterministic-generalization-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_hhs_pass124_parallel_deterministic_generalization_v1.py

.PHONY: test-pass125
test-pass125:
	python -m pytest -q tests/test_hhs_pass125_canonical_document_ingestion_v1.py

.PHONY: test-pass126
test-pass126:
	python -m pytest -q tests/test_hhs_pass126_document_claim_interpretation_v1.py

.PHONY: test-pass128
test-pass128:
	python -m pytest -q tests/test_hhs_pass128_canonical_knowledge_graph_retrieval_v1.py


.PHONY: pass135-ceuac-audit pass135-tests
pass135-ceuac-audit:
	python -m hhs_runtime.hhs_pass135_ceuac_audit_v1 run $(SUBJECT_ARCHIVE) release_artifacts/pass135

pass135-tests:
	python -m pytest -q tests/test_hhs_pass135_ceuac_audit_v1.py

.PHONY: test-pass145
test-pass145:
	python -m pytest -q tests/test_hhs_pass145_android_knowledge_enterprise_platform_v1.py

.PHONY: pass149 pass150 pass150-contract-matrix
pass149:
	python -m pytest -q tests/test_pass149_contract_executor.py
pass150:
	python -m pytest -q tests/test_pass150_hash216_genome.py tests/test_pass150_contract_matrix.py
pass150-contract-matrix:
	python -m pytest -q tests/test_pass150_contract_matrix.py

.PHONY: pass151-contract-governed-language pass152-universal-elastic-closure pass152-full
pass151-contract-governed-language:
	./tests/pass151/run_all.sh

pass152-universal-elastic-closure:
	./tests/pass152/run_all.sh

pass152-full:
	$(MAKE) pass151-contract-governed-language
	$(MAKE) pass152-universal-elastic-closure
	$(MAKE) verify-c
