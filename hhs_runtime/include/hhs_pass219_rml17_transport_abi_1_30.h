#ifndef HHS_PASS219_RML17_TRANSPORT_ABI_1_30_H
#define HHS_PASS219_RML17_TRANSPORT_ABI_1_30_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_MAJOR 1U
#define HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_MINOR 30U
#define HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_PATCH 0U

#define HHS_PASS219_RML17_TRANSPORT_OPERATION_COUNT 64U
#define HHS_PASS219_RML17_TRANSPORT_PHASE_COUNT 72U
#define HHS_PASS219_RML17_TRANSPORT_CELL_COUNT 81U
#define HHS_PASS219_RML17_TRANSPORT_DIRECTION_COUNT 4U
#define HHS_PASS219_RML17_TRANSPORT_NODE_COUNT UINT64_C(373248)
#define HHS_PASS219_RML17_TRANSPORT_ADDRESS_COUNT UINT64_C(1492992)

typedef struct HHSPass219RML17TransportAddressV1 {
    uint8_t operation64;
    uint8_t phase72;
    uint8_t cell81;
    uint8_t direction4;
} HHSPass219RML17TransportAddressV1;

typedef struct HHSPass219RML17TransportReportV1 {
    uint64_t node_count;
    uint64_t address_count;
    uint64_t discrete_divergence_nodes_checked;
    uint64_t reciprocal_edge_addresses_checked;
    uint64_t admission_preservation_addresses_checked;
    uint64_t zero_diffusion_addresses_checked;
    uint64_t composed_reverse_addresses_checked;
    uint64_t unique_target_addresses;
    uint64_t failure_count;
    uint8_t discrete_divergence_gate;
    uint8_t reciprocal_edge_balance_gate;
    uint8_t admission_preservation_gate;
    uint8_t zero_canonical_diffusion_gate;
    uint8_t composed_reverse_closure_gate;
    uint8_t exhaustive_address_coverage;
    uint8_t target_map_bijective;
    uint8_t exact_integer_phase_arithmetic;
    uint8_t canonical_transition_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_mint_authority;
    uint8_t canonical_hash216_persistence_authority;
    uint8_t pass;
} HHSPass219RML17TransportReportV1;

uint32_t hhs_pass219_rml17_transport_abi_version(void);
uint64_t hhs_pass219_rml17_transport_node_count(void);
uint64_t hhs_pass219_rml17_transport_address_count(void);

int hhs_pass219_rml17_transport_flatten(
    const HHSPass219RML17TransportAddressV1* address,
    uint64_t* out_index
);
int hhs_pass219_rml17_transport_unflatten(
    uint64_t index,
    HHSPass219RML17TransportAddressV1* out_address
);
int hhs_pass219_rml17_transport_signed_flux(uint8_t direction4, int8_t* out_flux);
int hhs_pass219_rml17_transport_reciprocal(uint8_t direction4, uint8_t* out_direction4);
int hhs_pass219_rml17_transport_successor(
    const HHSPass219RML17TransportAddressV1* source,
    HHSPass219RML17TransportAddressV1* out_target
);
int hhs_pass219_rml17_transport_zero_diffusion(
    const HHSPass219RML17TransportAddressV1* source,
    uint8_t* out_zero_diffusion
);
int hhs_pass219_rml17_transport_audit(HHSPass219RML17TransportReportV1* out_report);

/* This ABI is observational/execution support beneath RML17. It cannot commit
 * a transition, mutate VM81, mint Hash72, or persist Hash216 state. */
int hhs_pass219_rml17_transport_has_transition_authority(void);

#ifdef __cplusplus
}
#endif

#endif
