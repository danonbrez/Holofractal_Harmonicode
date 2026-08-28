#ifndef HHS_PASS219_INHERITED_PASS201_1_23_H
#define HHS_PASS219_INHERITED_PASS201_1_23_H

#include "hhs_pass219_inherited_pass202_1_22.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_MINOR 23U
#define HHS_EXACT_PASS219_INHERITED_PASS201_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS201_NUMBER 201U
#define HHS_EXACT_PASS201_PRIMARY_PR 142U
#define HHS_EXACT_PASS201_API_MODULE_COUNT 37U
#define HHS_EXACT_PASS201_IMPORTED_API_MODULE_COUNT 37U
#define HHS_EXACT_PASS201_IMPORT_FAILURE_COUNT 0U
#define HHS_EXACT_PASS201_ROUTER_COUNT 39U
#define HHS_EXACT_PASS201_ROUTER_ROUTE_COUNT 452U
#define HHS_EXACT_PASS201_EXISTING_ROUTE_COUNT 273U
#define HHS_EXACT_PASS201_ATTACHED_ROUTE_COUNT 179U
#define HHS_EXACT_PASS201_UNEXPOSED_ROUTE_COUNT 0U
#define HHS_EXACT_PASS201_PUBLIC_ROUTE_COUNT 449U
#define HHS_EXACT_PASS201_PUBLIC_SERVICE_COUNT 68U
#define HHS_EXACT_PASS201_PUBLIC_PASS_MODULE_COUNT 41U
#define HHS_EXACT_PASS201_OPENAPI_PATH_COUNT 421U
#define HHS_EXACT_PASS201_OPENAPI_MISSING_COUNT 0U
#define HHS_EXACT_PASS201_PUBLIC_ENDPOINT_PROBE_COUNT 12U
#define HHS_EXACT_PASS201_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS201_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass201PublicAPIFederationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t api_module_count;
    uint32_t imported_api_module_count;
    uint32_t import_failure_count;
    uint32_t router_count;
    uint32_t router_route_count;
    uint32_t existing_route_count;
    uint32_t attached_route_count;
    uint32_t unexposed_route_count;
    uint32_t public_route_count;
    uint32_t public_service_count;
    uint32_t public_pass_module_count;
    uint32_t openapi_path_count;
    uint32_t openapi_missing_count;
    uint32_t public_endpoint_probe_count;
    uint32_t api_router_enumeration_bound;
    uint32_t missing_only_attachment_bound;
    uint32_t existing_explicit_routes_preserved;
    uint32_t deterministic_route_identity_bound;
    uint32_t route_identity_is_index_only;
    uint32_t service_catalog_bound;
    uint32_t pass_catalog_bound;
    uint32_t openapi_projection_complete;
    uint32_t bounded_catalog_tool_interface;
    uint32_t arbitrary_python_execution_public;
    uint32_t native_route_authority_preserved;
    uint32_t public_routes_before_unknown_fallback;
    uint32_t static_root_last;
    uint32_t pass202_successor_preserved;
    uint32_t pass219_new_public_execution_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char primary_base_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char validated_executable_head[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char evidence_head_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char frozen_i122_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char workflow_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char runtime_v1_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char production_projection_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char public_routes_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char contract_test_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char production_validator_blob[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
} HHSExactPass201PublicAPIFederationWitnessV1;

typedef struct HHSExactPass219InheritedPass201BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t immutable_source_identity_bound;
    uint32_t router_closure_bound;
    uint32_t deterministic_catalog_bound;
    uint32_t bounded_tool_boundary_bound;
    uint32_t native_route_authority_preserved_bound;
    uint32_t pass202_successor_bound;
    uint32_t no_new_public_execution_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_public_execution_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_merge_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
    char frozen_i122_commit[HHS_EXACT_PASS201_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass201BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass201_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass201_public_api_federation(
    const HHSExactPass201PublicAPIFederationWitnessV1 *witness,
    HHSExactPass219InheritedPass201BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
