#ifndef HHS_PASS219_PASS169_RUNTIME_PROVIDER_1_21_13_H
#define HHS_PASS219_PASS169_RUNTIME_PROVIDER_1_21_13_H

#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_PATCH 13U

typedef struct HHSExactPass219Pass169RuntimeProviderDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t production_provider_implementation_present;
    uint8_t non_test_provider;
    uint8_t pass159_provenance_required;
    uint8_t full_symbolic_uqcel_probe_required;
    uint8_t full_symbolic_uqcel_supported;
    uint8_t local_p_snapshot_binding_supported;
    uint8_t canonical_gate_vector_export_supported;
    uint8_t canonical_authority_available;
    uint8_t test_fixture_authority;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_mint_authority;
    uint8_t hash216_persistence_authority;
    uint8_t reserved0[3];
} HHSExactPass219Pass169RuntimeProviderDescriptorV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_pass169_runtime_provider_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass169_runtime_provider_descriptor(
    HHSExactPass219Pass169RuntimeProviderDescriptorV1 *out_descriptor
);

/*
 * Production definition of the I121.11 provider symbol.
 *
 * I155 deliberately does not manufacture Pass169 truth.  It binds the exact
 * Pass159 provenance and probes the full-symbolic UQCEL runtime.  While the
 * aggregate monolithic residual remains unsupported it returns
 * HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN, which the I121.11 binder maps to a
 * valid UNRESOLVED/FULL_SYMBOLIC_UNRESOLVED state.
 */
HHSExactStatus hhs_pass169_verify_combined_gate_authority_1_21_11(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
);

#ifdef __cplusplus
}
#endif

#endif
