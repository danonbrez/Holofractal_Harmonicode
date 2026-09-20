#ifndef HHS_PASS219_LANE5_RAW_X86_VM5184_KERNEL_1_57_H
#define HHS_PASS219_LANE5_RAW_X86_VM5184_KERNEL_1_57_H

#include "hhs_pass219_global_raw5184_serialization_hydration_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_VERSION UINT32_C(0x00010139)
#define HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_FRAME_BYTES HHS_EXACT_VM81_FRAME_BYTES
#define HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_FRAME_BITS HHS_EXACT_VM81_FRAME_BITS
#define HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_LOCAL_STATES HHS_EXACT_PHASE_PAIR_COUNT

typedef struct HHSExactPass219Lane5RawX86VM5184DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t frame_bytes;
    uint32_t frame_bits;
    uint32_t vm81_cells;
    uint32_t local_states_per_cell;
    uint32_t vm5184_addresses;
    uint8_t direct_raw_x86_ingress;
    uint8_t direct_vm81_kernel_execution;
    uint8_t exact_raw_egress;
    uint8_t format_translation_layer;
    uint8_t floating_point_authority;
    uint8_t host_instruction_execution_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t reserved0[3];
} HHSExactPass219Lane5RawX86VM5184DescriptorV1;

typedef struct HHSExactPass219Lane5RawX86VM5184ReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t input_bytes;
    uint32_t output_bytes;
    uint32_t vm5184_addresses;
    uint32_t frames_processed;
    uint64_t state_step_count;
    uint64_t hydration_signature64;
    uint8_t exact_byte_identity;
    uint8_t direct_raw_x86_ingress;
    uint8_t direct_vm81_kernel_execution;
    uint8_t format_translation_layer;
    uint8_t floating_point_authority;
    uint8_t host_instruction_execution_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t reserved0;
} HHSExactPass219Lane5RawX86VM5184ReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_raw_x86_vm5184_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_descriptor(
    HHSExactPass219Lane5RawX86VM5184DescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_step(
    const uint8_t *input,
    size_t length,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    uint8_t *output,
    size_t capacity,
    size_t *out_length,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision,
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_stream(
    const uint8_t *input,
    size_t length,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    uint8_t *output,
    size_t capacity,
    size_t *out_length,
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
