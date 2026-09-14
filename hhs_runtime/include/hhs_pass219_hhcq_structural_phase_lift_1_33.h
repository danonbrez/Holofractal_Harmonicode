#ifndef HHS_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_1_33_H
#define HHS_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_1_33_H

#include "hhs_pass219b_phase_quantized_hydration_1_0.h"
#include "hhs_pass219_hhcq_symbolic_phase_gear_1_32.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION UINT32_C(0x00010021)
#define HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_COUNT UINT32_C(8)
#define HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_MASK UINT8_C(0xff)

typedef enum HHSExactPass219HHCQStructuralDirectionV1 {
    HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_REVERSE = -1,
    HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD = 1
} HHSExactPass219HHCQStructuralDirectionV1;

typedef struct HHSExactPass219HHCQStructuralPhaseDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass219b_phase_version;
    uint32_t symbolic_phase_version;
    uint32_t relation_role_count;
    uint32_t phase_origin_count;
    uint8_t pass219b_structural_source_required;
    uint8_t parent_hydration_coordinate_required;
    uint8_t complete_role_graph_required;
    uint8_t ring_step_basis_family_direction_required;
    uint8_t origin_relative_position_required;
    uint8_t tensor_source_required;
    uint8_t center_closure_required;
    uint8_t orientation_from_structural_direction;
    uint8_t raw_vm81_word_semantic_authority;
    uint8_t raw_phase_residue_semantic_authority;
    uint8_t scalar_phase_position_semantic_authority;
    uint8_t scalar_integer_semantic_authority;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[6];
} HHSExactPass219HHCQStructuralPhaseDescriptorV1;

typedef struct HHSExactPass219HHCQStructuralPhaseLiftV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219BPhaseCellV1 phase_cell;
    HHSExactPass219HHCQSymbolicCarrierV1 carrier;
    HHSExactPass219HHCQSymbolicManifoldV1 manifold;
    uint16_t prime_p;
    uint16_t prime_q;
    uint8_t base_resolution_index;
    uint8_t relation_role_mask;
    uint8_t xy_ring_orientation;
    uint8_t zw_ring_orientation;
    uint8_t structural_topology_exact;
    uint8_t parent_coordinate_exact;
    uint8_t relation_roles_exact;
    uint8_t ring_topology_exact;
    uint8_t phase_positions_exact;
    uint8_t tensor_source_preserved;
    uint8_t center_closure_preserved;
    uint8_t symbolic_carrier_admitted;
    uint8_t constraint_intersection_satisfied;
    uint8_t raw_vm81_word_semantic_authority;
    uint8_t raw_phase_residue_semantic_authority;
    uint8_t scalar_phase_position_semantic_authority;
    uint8_t scalar_integer_semantic_authority;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
    uint64_t structural_signature64;
} HHSExactPass219HHCQStructuralPhaseLiftV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_structural_phase_lift_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_descriptor(
    HHSExactPass219HHCQStructuralPhaseDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
    const HHSExactPass219BPhaseCellV1 *phase_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQStructuralPhaseLiftV1 *out_lift);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQStructuralPhaseLiftV1 *out_lift);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_validate(
    const HHSExactPass219HHCQStructuralPhaseLiftV1 *lift);

#ifdef __cplusplus
}
#endif

#endif
