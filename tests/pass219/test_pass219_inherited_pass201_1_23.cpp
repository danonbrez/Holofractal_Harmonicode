#include "hhs_pass219_inherited_pass201_1_23.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass201PublicAPIFederationWitnessV1 witness() {
    HHSExactPass201PublicAPIFederationWitnessV1 value{};
    value.struct_size = static_cast<uint32_t>(sizeof(value));
    value.version = hhs_exact_pass219_inherited_pass201_version();
    value.primary_pull_request = HHS_EXACT_PASS201_PRIMARY_PR;
    value.api_module_count = HHS_EXACT_PASS201_API_MODULE_COUNT;
    value.imported_api_module_count = HHS_EXACT_PASS201_IMPORTED_API_MODULE_COUNT;
    value.import_failure_count = HHS_EXACT_PASS201_IMPORT_FAILURE_COUNT;
    value.router_count = HHS_EXACT_PASS201_ROUTER_COUNT;
    value.router_route_count = HHS_EXACT_PASS201_ROUTER_ROUTE_COUNT;
    value.existing_route_count = HHS_EXACT_PASS201_EXISTING_ROUTE_COUNT;
    value.attached_route_count = HHS_EXACT_PASS201_ATTACHED_ROUTE_COUNT;
    value.unexposed_route_count = HHS_EXACT_PASS201_UNEXPOSED_ROUTE_COUNT;
    value.public_route_count = HHS_EXACT_PASS201_PUBLIC_ROUTE_COUNT;
    value.public_service_count = HHS_EXACT_PASS201_PUBLIC_SERVICE_COUNT;
    value.public_pass_module_count = HHS_EXACT_PASS201_PUBLIC_PASS_MODULE_COUNT;
    value.openapi_path_count = HHS_EXACT_PASS201_OPENAPI_PATH_COUNT;
    value.openapi_missing_count = HHS_EXACT_PASS201_OPENAPI_MISSING_COUNT;
    value.public_endpoint_probe_count = HHS_EXACT_PASS201_PUBLIC_ENDPOINT_PROBE_COUNT;
    value.api_router_enumeration_bound = 1U;
    value.missing_only_attachment_bound = 1U;
    value.existing_explicit_routes_preserved = 1U;
    value.deterministic_route_identity_bound = 1U;
    value.route_identity_is_index_only = 1U;
    value.service_catalog_bound = 1U;
    value.pass_catalog_bound = 1U;
    value.openapi_projection_complete = 1U;
    value.bounded_catalog_tool_interface = 1U;
    value.arbitrary_python_execution_public = 0U;
    value.native_route_authority_preserved = 1U;
    value.public_routes_before_unknown_fallback = 1U;
    value.static_root_last = 1U;
    value.pass202_successor_preserved = 1U;
    value.pass219_new_public_execution_authority = 0U;
    value.pass219_new_canonical_mutation_authority = 0U;
    value.pass219_new_persistence_authority = 0U;
    value.pass219_new_hash72_clock = 0U;
    value.cxx_mutation_authority = 0U;
    value.vm81_mutation_authority = 0U;
    std::memcpy(value.primary_base_commit, "0da486d86b55074baadd4a3e5cffb5f87893526b", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.validated_executable_head, "2f5299b44b6ee01af73e43a57d27cc7c6e2f7eda", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.evidence_head_commit, "f7fbd3007c7e08d5566e5176eb4eed955f44b739", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.accepted_merge_commit, "0e3f8a49b4a9b1e5b9b79e0dc73adebeef933f58", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.frozen_i122_commit, "a8d08be6d16722df6f42f1f88eef2a83f895107e", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.contract_blob, "88a34ca711b2b85dc8fa157a71125ce6d31919a8", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.workflow_blob, "0171e64ba9ef1228c05852fc51c375abed21abdd", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.runtime_v1_blob, "99a5b966b2885a24b5d3d1a47b39b3eb7060d211", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.production_projection_blob, "5b07f7369e702afef69358081d3ab67519dc91e1", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.public_routes_blob, "84e5acdcbea9c5f85ac38a1b792733c52b232edb", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.contract_test_blob, "da90ba15304e4fd73b987151b01c7db459f2f93c", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    std::memcpy(value.production_validator_blob, "0489ccba5d6d1b5a7ceda04c13621091ece8f3c7", HHS_EXACT_PASS201_GIT_SHA_STRLEN);
    return value;
}

int main() {
    auto value = witness();
    hhs::rna::InheritedPass201PublicAPIFederation binding(value);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.record().pass202_successor_bound == 1U);
    assert(binding.record().pass219_new_public_execution_authority == 0U);

    value = witness();
    value.arbitrary_python_execution_public = 1U;
    hhs::rna::InheritedPass201PublicAPIFederation generic_execution(value);
    assert(generic_execution.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!generic_execution.wired());

    value = witness();
    value.pass219_new_canonical_mutation_authority = 1U;
    hhs::rna::InheritedPass201PublicAPIFederation mutation(value);
    assert(mutation.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!mutation.wired());
    return 0;
}
