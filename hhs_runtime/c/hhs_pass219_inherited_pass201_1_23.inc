#include "../include/hhs_pass219_inherited_pass201_1_23.h"

#include <stddef.h>
#include <string.h>

static const char P201_PRIMARY_BASE[] = "0da486d86b55074baadd4a3e5cffb5f87893526b";
static const char P201_VALIDATED_EXECUTABLE_HEAD[] = "2f5299b44b6ee01af73e43a57d27cc7c6e2f7eda";
static const char P201_EVIDENCE_HEAD[] = "f7fbd3007c7e08d5566e5176eb4eed955f44b739";
static const char P201_ACCEPTED_MERGE[] = "0e3f8a49b4a9b1e5b9b79e0dc73adebeef933f58";
static const char P201_FROZEN_I122[] = "a8d08be6d16722df6f42f1f88eef2a83f895107e";
static const char P201_CONTRACT_BLOB[] = "88a34ca711b2b85dc8fa157a71125ce6d31919a8";
static const char P201_WORKFLOW_BLOB[] = "0171e64ba9ef1228c05852fc51c375abed21abdd";
static const char P201_RUNTIME_V1_BLOB[] = "99a5b966b2885a24b5d3d1a47b39b3eb7060d211";
static const char P201_PRODUCTION_PROJECTION_BLOB[] = "5b07f7369e702afef69358081d3ab67519dc91e1";
static const char P201_PUBLIC_ROUTES_BLOB[] = "84e5acdcbea9c5f85ac38a1b792733c52b232edb";
static const char P201_CONTRACT_TEST_BLOB[] = "da90ba15304e4fd73b987151b01c7db459f2f93c";
static const char P201_PRODUCTION_VALIDATOR_BLOB[] = "0489ccba5d6d1b5a7ceda04c13621091ece8f3c7";

static uint32_t p201_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_PATCH;
}

static int p201_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p201_git(const char value[HHS_EXACT_PASS201_GIT_SHA_STRLEN], const char *expected) {
    return p201_text(value, HHS_EXACT_PASS201_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS201_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass201_version(void) { return p201_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass201_public_api_federation(
    const HHSExactPass201PublicAPIFederationWitnessV1 *witness,
    HHSExactPass219InheritedPass201BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p201_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS201_PRIMARY_PR ||
        witness->api_module_count != HHS_EXACT_PASS201_API_MODULE_COUNT ||
        witness->imported_api_module_count != HHS_EXACT_PASS201_IMPORTED_API_MODULE_COUNT ||
        witness->import_failure_count != HHS_EXACT_PASS201_IMPORT_FAILURE_COUNT ||
        witness->router_count != HHS_EXACT_PASS201_ROUTER_COUNT ||
        witness->router_route_count != HHS_EXACT_PASS201_ROUTER_ROUTE_COUNT ||
        witness->existing_route_count != HHS_EXACT_PASS201_EXISTING_ROUTE_COUNT ||
        witness->attached_route_count != HHS_EXACT_PASS201_ATTACHED_ROUTE_COUNT ||
        witness->unexposed_route_count != HHS_EXACT_PASS201_UNEXPOSED_ROUTE_COUNT ||
        witness->public_route_count != HHS_EXACT_PASS201_PUBLIC_ROUTE_COUNT ||
        witness->public_service_count != HHS_EXACT_PASS201_PUBLIC_SERVICE_COUNT ||
        witness->public_pass_module_count != HHS_EXACT_PASS201_PUBLIC_PASS_MODULE_COUNT ||
        witness->openapi_path_count != HHS_EXACT_PASS201_OPENAPI_PATH_COUNT ||
        witness->openapi_missing_count != HHS_EXACT_PASS201_OPENAPI_MISSING_COUNT ||
        witness->public_endpoint_probe_count != HHS_EXACT_PASS201_PUBLIC_ENDPOINT_PROBE_COUNT ||
        witness->api_router_enumeration_bound != 1U ||
        witness->missing_only_attachment_bound != 1U ||
        witness->existing_explicit_routes_preserved != 1U ||
        witness->deterministic_route_identity_bound != 1U ||
        witness->route_identity_is_index_only != 1U ||
        witness->service_catalog_bound != 1U ||
        witness->pass_catalog_bound != 1U ||
        witness->openapi_projection_complete != 1U ||
        witness->bounded_catalog_tool_interface != 1U ||
        witness->arbitrary_python_execution_public != 0U ||
        witness->native_route_authority_preserved != 1U ||
        witness->public_routes_before_unknown_fallback != 1U ||
        witness->static_root_last != 1U ||
        witness->pass202_successor_preserved != 1U ||
        witness->pass219_new_public_execution_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p201_git(witness->primary_base_commit, P201_PRIMARY_BASE) ||
        !p201_git(witness->validated_executable_head, P201_VALIDATED_EXECUTABLE_HEAD) ||
        !p201_git(witness->evidence_head_commit, P201_EVIDENCE_HEAD) ||
        !p201_git(witness->accepted_merge_commit, P201_ACCEPTED_MERGE) ||
        !p201_git(witness->frozen_i122_commit, P201_FROZEN_I122) ||
        !p201_git(witness->contract_blob, P201_CONTRACT_BLOB) ||
        !p201_git(witness->workflow_blob, P201_WORKFLOW_BLOB) ||
        !p201_git(witness->runtime_v1_blob, P201_RUNTIME_V1_BLOB) ||
        !p201_git(witness->production_projection_blob, P201_PRODUCTION_PROJECTION_BLOB) ||
        !p201_git(witness->public_routes_blob, P201_PUBLIC_ROUTES_BLOB) ||
        !p201_git(witness->contract_test_blob, P201_CONTRACT_TEST_BLOB) ||
        !p201_git(witness->production_validator_blob, P201_PRODUCTION_VALIDATOR_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p201_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS201_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->immutable_source_identity_bound = 1U;
    out_binding->router_closure_bound = 1U;
    out_binding->deterministic_catalog_bound = 1U;
    out_binding->bounded_tool_boundary_bound = 1U;
    out_binding->native_route_authority_preserved_bound = 1U;
    out_binding->pass202_successor_bound = 1U;
    out_binding->no_new_public_execution_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_public_execution_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i122_commit, witness->frozen_i122_commit, HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
