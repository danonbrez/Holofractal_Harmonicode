#ifndef HHS_PASS219_LANE5_VIRTUAL_BIOS_CONTROL_PLANE_1_58_H
#define HHS_PASS219_LANE5_VIRTUAL_BIOS_CONTROL_PLANE_1_58_H

#include "hhs_pass219_global_raw5184_serialization_hydration_1_0.h"
#include "hhs_pass219_core_holographic_four_lane_1_24.h"
#include "hhs_pass219_global_latency_policy_25_3_1_0.h"
#include "hhs_pass219_lane5_hash216_composition_jump_store_1_38.h"
#include "hhs_pass219_lane5_automatic_superedge_routing_1_42.h"
#include "hhs_pass219_lane5_direct_witness_routing_1_46.h"
#include "hhs_pass219_lane5_unbounded_workload_scaling_1_48.h"
#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_VIRTUAL_BIOS_VERSION UINT32_C(0x0001013A)

typedef struct HHSExactPass219Lane5VirtualBIOSDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t vm81_cells;
    uint32_t local_constructor_states;
    uint32_t vm5184_bits;
    uint32_t raw_frame_bytes;
    uint32_t hydration_lanes;
    uint32_t phase_modulus;

    uint8_t resident_vm_bios;
    uint8_t control_plane_only;
    uint8_t payload_dataflow_stage;
    uint8_t payload_format_translation;
    uint8_t raw_x86_vm5184_kernel_bound;
    uint8_t cpp_rna_cell_wall_bound;
    uint8_t pqc_firewall_bound;
    uint8_t four_lane_hydration_bound;
    uint8_t global_latency_policy_bound;
    uint8_t direct_witness_routing_bound;
    uint8_t automatic_superedge_routing_bound;
    uint8_t unbounded_workload_routing_bound;
    uint8_t hash216_validated_jump_cache_bound;
    uint8_t candidate_optimization_only;
    uint8_t signed_vm81_admission_required;
    uint8_t hash72_commit_bypass_allowed;
    uint8_t hash216_cache_commit_bypass_allowed;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t host_instruction_execution_authority;
    uint8_t reserved0;
} HHSExactPass219Lane5VirtualBIOSDescriptorV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_virtual_bios_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_virtual_bios_descriptor(
    HHSExactPass219Lane5VirtualBIOSDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_virtual_bios_validate(void);

#ifdef __cplusplus
}
#endif

#endif
