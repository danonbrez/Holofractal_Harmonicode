#ifndef HHS_PASS219_LANE5_T5184_PHASE_SUPPORT_1_49_H
#define HHS_PASS219_LANE5_T5184_PHASE_SUPPORT_1_49_H

#include "hhs_pass219_lane5_unbounded_workload_scaling_1_48.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_VERSION UINT32_C(0x00010031)
#define HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_NAMESPACE UINT32_C(0x00021931)
#define HHS_EXACT_PASS219_LANE5_T5184_OPERATION64 UINT32_C(64)
#define HHS_EXACT_PASS219_LANE5_T5184_VM81_CELLS UINT32_C(81)
#define HHS_EXACT_PASS219_LANE5_T5184_TOTAL_POSITIONS UINT32_C(5184)
#define HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL UINT32_C(16)
#define HHS_EXACT_PASS219_LANE5_T5184_BYPASS_PER_CELL UINT32_C(48)
#define HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_VM81 UINT32_C(1296)
#define HHS_EXACT_PASS219_LANE5_T5184_BYPASS_VM81 UINT32_C(3888)
#define HHS_EXACT_PASS219_LANE5_T5184_PAIR_COUNT_VM81 UINT32_C(324)
#define HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_MASK UINT64_C(0x0f00f000000f00f0)

enum HHSExactPass219Lane5T5184PhaseCodeV1 {
    HHS_EXACT_PASS219_LANE5_T5184_PHASE_NONE = 0,
    HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY = 1,
    HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX = 2,
    HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW = 3,
    HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ = 4
};

typedef struct HHSExactPass219Lane5T5184PhaseSupportAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t operation64;
    uint32_t vm81_cells;
    uint32_t total_positions;
    uint32_t support_per_cell;
    uint32_t bypass_per_cell;
    uint32_t support_vm81;
    uint32_t bypass_vm81;
    uint32_t pair_count_vm81;
    uint64_t phase_support_mask64;
    uint8_t one_quarter_phase_support;
    uint8_t three_quarter_phase_bypass;
    uint8_t support_equals_36_squared;
    uint8_t support_equals_18_times_72;
    uint8_t pair_count_equals_18_squared;
    uint8_t ordered_products_preserved;
    uint8_t wire_mirror_xy_equals_zw;
    uint8_t wire_mirror_yx_equals_wz;
    uint8_t q_minus_one_sign_preserved;
    uint8_t support_table_direct_iteration;
    uint8_t full_state_identity_still_required;
    uint8_t serialized_operand_binding_still_required;
    uint8_t candidate_only;
    uint8_t requires_exact_cpu_vm81_replay;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[5];
} HHSExactPass219Lane5T5184PhaseSupportAuthorityV1;

typedef struct HHSExactPass219Lane5T5184PhaseSlotV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t vm81_cell;
    uint32_t local64;
    uint32_t global5184;
    uint32_t support_ordinal;
    uint8_t phase_bearing;
    uint8_t phase_code;
    int8_t phase_sign;
    uint8_t representative_phase_code;
    uint8_t requires_phase_specific_check;
    uint8_t full_state_identity_required;
    uint8_t candidate_only;
    uint8_t reserved0;
} HHSExactPass219Lane5T5184PhaseSlotV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_t5184_phase_support_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_authority(
    HHSExactPass219Lane5T5184PhaseSupportAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_local64(
    uint32_t support_ordinal,
    uint32_t *out_local64
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_classify(
    uint32_t vm81_cell,
    uint32_t local64,
    HHSExactPass219Lane5T5184PhaseSlotV1 *out_slot
);

#ifdef __cplusplus
}
#endif

#endif
