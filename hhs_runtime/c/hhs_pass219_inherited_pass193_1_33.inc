#include "../include/hhs_pass219_inherited_pass193_1_33.h"

#include <stddef.h>
#include <string.h>

static const char P193_AUTHORIZATION_COMMIT[] = "eebc47a52de143df4a9acf807735f576ad0ce844";
static const char P193_BASELINE_COMMIT[] = "c3da7e2b7125754b65f08fb8922a151bf01df2b8";
static const char P193_FROZEN_I132[] = "d311cd243845456851518ce1fef026a7d3cac45e";
static const char P193_CONTRACT_BLOB[] = "2452a5d5184bd9275e150b4b4afd840928e723fd";
static const char P193_PRECONTRACT_TEST_BLOB[] = "a72e7b8ab6dc0f891540fe2192d92d80f4a0cf52";
static const char P193_PASS192_REFERENCE_BLOB[] = "bda83c1a8791dd4bd9e807a88e0a419848d1d140";
static const char P193_RUNTIME_BLOB[] = "c5c961b406a67c75f277299c4c617c15bb4544cf";
static const char P193_API_BLOB[] = "76482bce7fa1d9940df05b86603ccf43db8bacb2";
static const char P193_RUNTIME_TEST_BLOB[] = "c003362aabf2a7a8cc7b2c9fc424b398b96f7050";
static const char P193_API_TEST_BLOB[] = "28abf4097fa5cb2ea7aeaaaded896d5eb6f02cd3";
static const char P193_NATIVE_TARGET_TEST_BLOB[] = "21c9d05101b42fd32eecda5f95aafbae0772b7af";
static const char P193_FOCUSED_WORKFLOW_BLOB[] = "7339e2f00a7af376a9ba1d9c6a27ca8f4b03e0be";

static uint32_t p193_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_PATCH;
}

static int p193_git(
    const char value[HHS_EXACT_PASS193_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS193_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS193_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass193_version(void) {
    return p193_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass193_hypersolid_native_egress(
    const HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass193BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p193_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->exact_hypersolid_registry != 1U ||
        witness->regular_family_classification != 1U ||
        witness->incidence_graph_identity != 1U ||
        witness->exact_or_symbolic_coordinate_authority != 1U ||
        witness->ordered_rational_phase_history != 1U ||
        witness->pass192_fibonacci_nesting != 1U ||
        witness->deterministic_fractal_address != 1U ||
        witness->noncanonical_projection_separation != 1U ||
        witness->vm81_authorized_canonical_mutations != 1U ||
        witness->hash72_mutation_receipt_chain != 1U ||
        witness->hash216_canonical_identity != 1U ||
        witness->native_artifact_provenance != 1U ||
        witness->linux_x86_64_compile_link_launch_abi_replay != 1U ||
        witness->linux_arm64_compile_link_launch_abi_replay != 1U ||
        witness->path_safe_portable_zip != 1U ||
        witness->explicit_user_action_install_boundary != 1U ||
        witness->nft_identity_execution_authorization_separation != 1U ||
        witness->reversible_url_safe_hash216_transport != 1U ||
        witness->pass194_successor_preserved != 1U ||
        witness->float_is_canonical_authority != 0U ||
        witness->projection_is_canonical_authority != 0U ||
        witness->package_autoexec_authority != 0U ||
        witness->nft_identity_is_execution_authority != 0U ||
        witness->native_target_evidence_is_vm81_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p193_git(witness->contract_authorization_commit, P193_AUTHORIZATION_COMMIT) ||
        !p193_git(witness->contract_baseline_commit, P193_BASELINE_COMMIT) ||
        !p193_git(witness->frozen_i132_commit, P193_FROZEN_I132) ||
        !p193_git(witness->contract_blob, P193_CONTRACT_BLOB) ||
        !p193_git(witness->precontract_test_blob, P193_PRECONTRACT_TEST_BLOB) ||
        !p193_git(witness->pass192_reference_blob, P193_PASS192_REFERENCE_BLOB) ||
        !p193_git(witness->runtime_blob, P193_RUNTIME_BLOB) ||
        !p193_git(witness->api_blob, P193_API_BLOB) ||
        !p193_git(witness->runtime_test_blob, P193_RUNTIME_TEST_BLOB) ||
        !p193_git(witness->api_test_blob, P193_API_TEST_BLOB) ||
        !p193_git(witness->native_target_test_blob, P193_NATIVE_TARGET_TEST_BLOB) ||
        !p193_git(witness->focused_workflow_blob, P193_FOCUSED_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p193_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS193_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->exact_geometry_bound = 1U;
    out_binding->ordered_phase_bound = 1U;
    out_binding->pass192_nesting_bound = 1U;
    out_binding->fractal_address_bound = 1U;
    out_binding->projection_separation_bound = 1U;
    out_binding->inherited_vm81_receipt_bound = 1U;
    out_binding->hash216_identity_bound = 1U;
    out_binding->native_target_validation_bound = 1U;
    out_binding->portable_package_security_bound = 1U;
    out_binding->nft_execution_separation_bound = 1U;
    out_binding->pass194_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->projection_is_canonical_authority = 0U;
    out_binding->package_autoexec_authority = 0U;
    out_binding->nft_identity_is_execution_authority = 0U;
    out_binding->native_target_evidence_is_vm81_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(
        out_binding->contract_authorization_commit,
        witness->contract_authorization_commit,
        HHS_EXACT_PASS193_GIT_SHA_STRLEN
    );
    memcpy(
        out_binding->frozen_i132_commit,
        witness->frozen_i132_commit,
        HHS_EXACT_PASS193_GIT_SHA_STRLEN
    );
    return HHS_EXACT_STATUS_OK;
}
