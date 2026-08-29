#include "hhs_pass219_inherited_pass193_1_33.h"

#include <assert.h>
#include <string.h>

static HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1 witness(void) {
    HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass193_version();
    w.exact_hypersolid_registry = 1U;
    w.regular_family_classification = 1U;
    w.incidence_graph_identity = 1U;
    w.exact_or_symbolic_coordinate_authority = 1U;
    w.ordered_rational_phase_history = 1U;
    w.pass192_fibonacci_nesting = 1U;
    w.deterministic_fractal_address = 1U;
    w.noncanonical_projection_separation = 1U;
    w.vm81_authorized_canonical_mutations = 1U;
    w.hash72_mutation_receipt_chain = 1U;
    w.hash216_canonical_identity = 1U;
    w.native_artifact_provenance = 1U;
    w.linux_x86_64_compile_link_launch_abi_replay = 1U;
    w.linux_arm64_compile_link_launch_abi_replay = 1U;
    w.path_safe_portable_zip = 1U;
    w.explicit_user_action_install_boundary = 1U;
    w.nft_identity_execution_authorization_separation = 1U;
    w.reversible_url_safe_hash216_transport = 1U;
    w.production_router_registered = 1U;
    w.public_api_federation_preserved = 1U;
    w.pass194_successor_preserved = 1U;
    strcpy(w.contract_authorization_commit, "eebc47a52de143df4a9acf807735f576ad0ce844");
    strcpy(w.contract_baseline_commit, "c3da7e2b7125754b65f08fb8922a151bf01df2b8");
    strcpy(w.frozen_i132_commit, "d311cd243845456851518ce1fef026a7d3cac45e");
    strcpy(w.contract_blob, "2452a5d5184bd9275e150b4b4afd840928e723fd");
    strcpy(w.precontract_test_blob, "a72e7b8ab6dc0f891540fe2192d92d80f4a0cf52");
    strcpy(w.pass192_reference_blob, "bda83c1a8791dd4bd9e807a88e0a419848d1d140");
    strcpy(w.runtime_blob, "c5c961b406a67c75f277299c4c617c15bb4544cf");
    strcpy(w.api_blob, "76482bce7fa1d9940df05b86603ccf43db8bacb2");
    strcpy(w.visual_server_blob, "d09fa35a4033e2c7576f11cdd0ac2f5f7b46ea1b");
    strcpy(w.runtime_test_blob, "c003362aabf2a7a8cc7b2c9fc424b398b96f7050");
    strcpy(w.api_test_blob, "28abf4097fa5cb2ea7aeaaaded896d5eb6f02cd3");
    strcpy(w.native_target_test_blob, "21c9d05101b42fd32eecda5f95aafbae0772b7af");
    strcpy(w.visual_registration_test_blob, "af461a5be0b8148c941b5fa0e3e78fe10d325dba");
    strcpy(w.focused_workflow_blob, "1d6e216f6f4b7dc6666906a8f50f379b8ef7d089");
    return w;
}

int main(void) {
    HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass193BindingV1 binding;
    assert(hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 193U);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.exact_geometry_bound == 1U);
    assert(binding.ordered_phase_bound == 1U);
    assert(binding.pass192_nesting_bound == 1U);
    assert(binding.fractal_address_bound == 1U);
    assert(binding.projection_separation_bound == 1U);
    assert(binding.inherited_vm81_receipt_bound == 1U);
    assert(binding.hash216_identity_bound == 1U);
    assert(binding.native_target_validation_bound == 1U);
    assert(binding.portable_package_security_bound == 1U);
    assert(binding.nft_execution_separation_bound == 1U);
    assert(binding.production_registration_bound == 1U);
    assert(binding.pass194_successor_bound == 1U);
    assert(binding.no_new_authority_bound == 1U);
    assert(binding.float_is_canonical_authority == 0U);
    assert(binding.projection_is_canonical_authority == 0U);
    assert(binding.package_autoexec_authority == 0U);
    assert(binding.nft_identity_is_execution_authority == 0U);
    assert(binding.native_target_evidence_is_vm81_authority == 0U);
    assert(binding.pass219_new_candidate_authority == 0U);
    assert(binding.pass219_new_canonical_mutation_authority == 0U);
    assert(binding.pass219_new_persistence_authority == 0U);
    assert(binding.pass219_new_hash72_clock == 0U);
    assert(binding.cxx_mutation_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness();
    w.production_router_registered = 0U;
    assert(hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.float_is_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.nft_identity_is_execution_authority = 1U;
    assert(hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.visual_server_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
