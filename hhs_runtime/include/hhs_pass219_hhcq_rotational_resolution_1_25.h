#ifndef HHS_PASS219_HHCQ_ROTATIONAL_RESOLUTION_1_25_H
#define HHS_PASS219_HHCQ_ROTATIONAL_RESOLUTION_1_25_H

#include "hhs_pass219_core_holographic_four_lane_1_24.h"
#include "hhs_pass219_octonion_runtime_1_19.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION UINT32_C(0x00010019)
#define HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT UINT32_C(5184)
#define HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT UINT32_C(35)
#define HHS_EXACT_PASS219_HHCQ_TRINARY_STEP UINT32_C(5)

typedef struct HHSExactPass219HHCQResolutionDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t parameter_count;
    uint32_t phase_modulus;
    uint32_t divisor_count;
    uint32_t trinary_step;
    uint8_t complete_2a3b_divisor_lattice;
    uint8_t ordered_xz_over_yw_phase_quotient;
    uint8_t dyadic_trinary_dual_primitive;
    uint8_t exact_orthogonal_decomposition;
    uint8_t core_equation_constructor_bound;
    uint8_t u72_rotational_ring;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219HHCQResolutionDescriptorV1;

typedef struct HHSExactPass219HHCQResolutionSelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t x_phase72;
    uint8_t y_phase72;
    uint8_t z_phase72;
    uint8_t w_phase72;
    int8_t trinary_direction;
    uint8_t xz_phase72;
    uint8_t yw_phase72;
    uint8_t quotient_phase72;
    uint8_t rotated_phase72;
    uint8_t resolution_index;
    uint16_t resolution_parameters;
    uint16_t region_count;
    uint8_t xz_orientation;
    uint8_t yw_orientation;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0;
    uint64_t selection_signature64;
} HHSExactPass219HHCQResolutionSelectionV1;

typedef struct HHSExactPass219HHCQParameterCoordinateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t parameter_index;
    uint16_t region_index;
    uint16_t local_offset;
    uint16_t region_start;
    uint16_t resolution_parameters;
    uint16_t region_count;
    uint8_t exact_integer_only;
    uint8_t reserved0[5];
} HHSExactPass219HHCQParameterCoordinateV1;

typedef struct HHSExactPass219HHCQRoundtripReportV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t parameters_visited;
    uint16_t resolution_parameters;
    uint16_t region_count;
    uint64_t input_signature64;
    uint64_t output_signature64;
    uint64_t decomposition_signature64;
    uint8_t orthogonal_partition_complete;
    uint8_t no_overlap;
    uint8_t no_gap;
    uint8_t exact_recomposition;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
} HHSExactPass219HHCQRoundtripReportV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_resolution_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_resolution_descriptor(
    HHSExactPass219HHCQResolutionDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_resolution_divisor(
    uint8_t resolution_index,
    uint16_t *out_parameters);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_resolution_select(
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t z_phase72,
    uint8_t w_phase72,
    int8_t trinary_direction,
    HHSExactPass219HHCQResolutionSelectionV1 *out_selection);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_parameter_locate(
    const HHSExactPass219HHCQResolutionSelectionV1 *selection,
    uint16_t parameter_index,
    HHSExactPass219HHCQParameterCoordinateV1 *out_coordinate);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_decompose_recompose(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219HHCQResolutionSelectionV1 *selection,
    HHSExactVM81Frame *out_frame,
    HHSExactPass219HHCQRoundtripReportV1 *out_report);

#ifdef __cplusplus
}
#endif

#endif
