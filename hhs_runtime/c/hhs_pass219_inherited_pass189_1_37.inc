#include "../include/hhs_pass219_inherited_pass189_1_37.h"

#include <stddef.h>
#include <string.h>

static const char P189_I137_TEMPLATE_CONTRACT_COMMIT[] = "9dfd373d5ccd66b9172313b750c8439435d90f49";
static const char P189_I137_HQLH_CONTRACT_MERGE[] = "54ffe9d89d1aa928a6be75a3663ad51f709b7b9d";
static const char P189_I137_RUNTIME_COMMIT[] = "a1a55a4f621ff3678f5af81119439e9558cf9db4";
static const char P189_I137_ITERATION2_COMMIT[] = "c3cc477cd1b573eb5a318c7f38a1197e428d7014";
static const char P189_I137_ITERATION3_COMMIT[] = "f3ceba745ce5b478ca850c14a543a18189cc7d6c";
static const char P189_I137_ITERATION4_COMMIT[] = "7a99674997974262b171a0aee05665cbeab42ab9";
static const char P189_I137_TOKEN_LIFECYCLE_COMMIT[] = "0ee579aa574fa8f8b4c827518ae4249bbad4e8be";
static const char P189_I137_DNS_INTEGRATION_COMMIT[] = "8ac51f5de0be323513577863fcbde71578ef4e14";
static const char P189_I137_FROZEN_I136[] = "3a76667eb463f8027e2bfaea4a2f76cff470c564";

static const char P189_I137_TEMPLATE_CONTRACT_BLOB[] = "daae3c4cb368d42fd9f83c22abd9a81380ba0f2a";
static const char P189_I137_HQLH_CONTRACT_BLOB[] = "0bc9f1a3ee9d2252002310e5c5cab88ad98553a5";
static const char P189_I137_RUNTIME_DOC_BLOB[] = "3d9a4f7869b23d2655c1027fac353c841a8b7a2e";
static const char P189_I137_ITERATION2_DOC_BLOB[] = "492c28b6368d7f36649e377cb052097a6fa60703";
static const char P189_I137_ITERATION3_DOC_BLOB[] = "492e5434c4319b28a9f8838606cfd8dc00b0ae65";
static const char P189_I137_ITERATION4_DOC_BLOB[] = "5c7e8391a28c14ae0bbdae15592d3889c85f53c0";
static const char P189_I137_MAKEFILE_BLOB[] = "35f9ed59c26994247a2fa209afe0280329cef106";
static const char P189_I137_NATIVE_HEADER_BLOB[] = "b558c7f090913a70bf3691f6fb413fd5a7bdebff";
static const char P189_I137_NATIVE_SOURCE_BLOB[] = "651a2a2f4be6d802c88182c016657be1698f83b2";
static const char P189_I137_PYTHON_RUNTIME_BLOB[] = "5d98e213ce80f793b0d3761efbe88dff33bb7f14";
static const char P189_I137_ITERATION2_PYTHON_BLOB[] = "88f50add4b71c9c57877f96f61854aade405c0b3";
static const char P189_I137_ITERATION3_PYTHON_BLOB[] = "eea7c2f825583d4013395c472d62cf9dd81e5923";
static const char P189_I137_ITERATION4_PYTHON_BLOB[] = "aeec45db0b773364fdc155be62499cbb5ec4e221";
static const char P189_I137_TOKEN_LIFECYCLE_BLOB[] = "b427718ba16e143797c0856587ec83556314df19";
static const char P189_I137_TEMPLATE_REGISTRY_BLOB[] = "8583c4e2e3621072d414448968cbdbfe81e311ad";
static const char P189_I137_FOCUSED_WORKFLOW_BLOB[] = "f184f462b5eb1a93fd3c41d2b622ee4ac0bcc35c";
static const char P189_I137_BASE_RECEIPT_BLOB[] = "23d61fa5cc157fcb44967e33956bbc97d50dba36";
static const char P189_I137_ITERATION2_RECEIPT_BLOB[] = "2e99a7a11e1adca6168ba10ad51cb6bf9d96b487";
static const char P189_I137_ITERATION3_RECEIPT_BLOB[] = "c0ef0202fda59f93581da4cad3f6ec163b7feb0a";
static const char P189_I137_ITERATION4_RECEIPT_BLOB[] = "c383e5232d1d16ba2b9f66cbe9a7bda09e432d9d";
static const char P189_I137_DNS_REGISTRY_BLOB[] = "16a264268f91301ba499c8beb253b18677873390";

static uint32_t p189_i137_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_PATCH;
}

static int p189_i137_git(
    const char value[HHS_EXACT_PASS189_I137_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS189_I137_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS189_I137_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass189_version(void) {
    return p189_i137_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass189_cumulative_authority(
    const HHSExactPass189CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass189BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p189_i137_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->template_registry_contract_preserved != 1U ||
        witness->hqlh_contract_preserved != 1U ||
        witness->runtime_implementation_preserved != 1U ||
        witness->iteration2_calibration_preserved != 1U ||
        witness->iteration3_adapter_preserved != 1U ||
        witness->iteration4_provenance_preserved != 1U ||
        witness->token_lifecycle_preserved != 1U ||
        witness->contextual_address_count != 51648192U ||
        witness->lo_shu_xnor_ternary_bound != 1U ||
        witness->hash72_receipt_chain != 1U ||
        witness->hash216_topology_identity != 1U ||
        witness->deterministic_replay != 1U ||
        witness->calibration_in_progress != 1U ||
        witness->measured_evidence_required_for_physical_candidate != 1U ||
        witness->real_hardware_execution_authorized != 0U ||
        witness->software_test_adapters_only != 1U ||
        witness->bounded_operator_leases != 1U ||
        witness->anti_replay_commands != 1U ||
        witness->payload_bound_quarantine != 1U ||
        witness->dual_approval_promotion != 1U ||
        witness->promotion_token_lifecycle != 1U ||
        witness->deterministic_rollback != 1U ||
        witness->sqlite_persistence != 1U ||
        witness->checkpoint_recovery != 1U ||
        witness->dns_port_separation_bound != 1U ||
        witness->pass190_successor_preserved != 1U ||
        witness->vercel_authority != 0U ||
        witness->external_digitalocean_mutation_claimed != 0U ||
        witness->float_is_canonical_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p189_i137_git(witness->template_contract_commit, P189_I137_TEMPLATE_CONTRACT_COMMIT) ||
        !p189_i137_git(witness->hqlh_contract_merge, P189_I137_HQLH_CONTRACT_MERGE) ||
        !p189_i137_git(witness->runtime_implementation_commit, P189_I137_RUNTIME_COMMIT) ||
        !p189_i137_git(witness->iteration2_commit, P189_I137_ITERATION2_COMMIT) ||
        !p189_i137_git(witness->iteration3_commit, P189_I137_ITERATION3_COMMIT) ||
        !p189_i137_git(witness->iteration4_commit, P189_I137_ITERATION4_COMMIT) ||
        !p189_i137_git(witness->token_lifecycle_commit, P189_I137_TOKEN_LIFECYCLE_COMMIT) ||
        !p189_i137_git(witness->dns_integration_commit, P189_I137_DNS_INTEGRATION_COMMIT) ||
        !p189_i137_git(witness->frozen_i136_commit, P189_I137_FROZEN_I136) ||
        !p189_i137_git(witness->template_contract_blob, P189_I137_TEMPLATE_CONTRACT_BLOB) ||
        !p189_i137_git(witness->hqlh_contract_blob, P189_I137_HQLH_CONTRACT_BLOB) ||
        !p189_i137_git(witness->runtime_doc_blob, P189_I137_RUNTIME_DOC_BLOB) ||
        !p189_i137_git(witness->iteration2_doc_blob, P189_I137_ITERATION2_DOC_BLOB) ||
        !p189_i137_git(witness->iteration3_doc_blob, P189_I137_ITERATION3_DOC_BLOB) ||
        !p189_i137_git(witness->iteration4_doc_blob, P189_I137_ITERATION4_DOC_BLOB) ||
        !p189_i137_git(witness->makefile_blob, P189_I137_MAKEFILE_BLOB) ||
        !p189_i137_git(witness->native_header_blob, P189_I137_NATIVE_HEADER_BLOB) ||
        !p189_i137_git(witness->native_source_blob, P189_I137_NATIVE_SOURCE_BLOB) ||
        !p189_i137_git(witness->python_runtime_blob, P189_I137_PYTHON_RUNTIME_BLOB) ||
        !p189_i137_git(witness->iteration2_python_blob, P189_I137_ITERATION2_PYTHON_BLOB) ||
        !p189_i137_git(witness->iteration3_python_blob, P189_I137_ITERATION3_PYTHON_BLOB) ||
        !p189_i137_git(witness->iteration4_python_blob, P189_I137_ITERATION4_PYTHON_BLOB) ||
        !p189_i137_git(witness->token_lifecycle_blob, P189_I137_TOKEN_LIFECYCLE_BLOB) ||
        !p189_i137_git(witness->template_registry_blob, P189_I137_TEMPLATE_REGISTRY_BLOB) ||
        !p189_i137_git(witness->focused_workflow_blob, P189_I137_FOCUSED_WORKFLOW_BLOB) ||
        !p189_i137_git(witness->base_receipt_blob, P189_I137_BASE_RECEIPT_BLOB) ||
        !p189_i137_git(witness->iteration2_receipt_blob, P189_I137_ITERATION2_RECEIPT_BLOB) ||
        !p189_i137_git(witness->iteration3_receipt_blob, P189_I137_ITERATION3_RECEIPT_BLOB) ||
        !p189_i137_git(witness->iteration4_receipt_blob, P189_I137_ITERATION4_RECEIPT_BLOB) ||
        !p189_i137_git(witness->dns_registry_blob, P189_I137_DNS_REGISTRY_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p189_i137_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS189_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->template_registry_bound = 1U;
    out_binding->hqlh_runtime_bound = 1U;
    out_binding->calibration_boundary_bound = 1U;
    out_binding->adapter_authority_bound = 1U;
    out_binding->provenance_authority_bound = 1U;
    out_binding->token_lifecycle_bound = 1U;
    out_binding->exact_topology_bound = 1U;
    out_binding->inherited_vm81_receipt_bound = 1U;
    out_binding->hardware_nonexecution_bound = 1U;
    out_binding->deployment_boundary_bound = 1U;
    out_binding->pass190_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->calibration_in_progress = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->frozen_i136_commit, witness->frozen_i136_commit, HHS_EXACT_PASS189_I137_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
