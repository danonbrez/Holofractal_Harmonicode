#ifndef HHS_PASS219_LANE5_VM5184_HASH216_TRAINING_C_ABI_1_73_H
#define HHS_PASS219_LANE5_VM5184_HASH216_TRAINING_C_ABI_1_73_H

#include "hhs_hash216.h"
#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_TRAINING_C_ABI_VERSION UINT32_C(0x00010049)
#define HHS_EXACT_PASS219_LANE5_TRAINING_METHOD_ID_BYTES UINT32_C(48)
#define HHS_EXACT_PASS219_LANE5_TRAINING_METHOD_COUNT UINT32_C(18)

typedef struct HHSExactPass219Lane5TrainingMethodV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t mode;
    uint32_t temporal;
    uint32_t primary_target;
    uint32_t target_mask;
    char method_id[HHS_EXACT_PASS219_LANE5_TRAINING_METHOD_ID_BYTES];
    uint8_t requires_oracle;
    uint8_t requires_negative_controls;
    uint8_t requires_replay;
    uint8_t preserves_ingress_egress;
    uint8_t routes_through_vm5184;
    uint8_t emits_candidate_hash216;
    uint8_t candidate_only;
    uint8_t natural_language_native;
    uint8_t ethical_text_supervisor;
    uint8_t reserved0[7];
} HHSExactPass219Lane5TrainingMethodV1;

typedef struct HHSExactPass219Lane5TrainingSpecimenV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t mode;
    uint32_t temporal;
    uint32_t target;
    uint32_t reserved0;
    char source_identity216[HHS_HASH216_LEN + 1];
    char oracle_identity216[HHS_HASH216_LEN + 1];
    char ethical_text_supervisor_identity216[HHS_HASH216_LEN + 1];
    uint64_t adapter_signature64;
    uint64_t executor_signature64;
    uint64_t validator_signature64;
    uint64_t negative_control_signature64;
    uint64_t replay_signature64;
    uint64_t ethical_text_supervisor_signature64;
    uint8_t oracle_verified;
    uint8_t negative_controls_verified;
    uint8_t replay_verified;
    uint8_t ingress_egress_preserved;
    uint8_t candidate_only_acknowledged;
    uint8_t natural_language_training;
    uint8_t ethical_text_supervision_verified;
    uint8_t reserved1;
} HHSExactPass219Lane5TrainingSpecimenV1;

typedef struct HHSExactPass219Lane5TrainingReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t mode;
    uint32_t temporal;
    uint32_t target;
    uint32_t method_index;
    uint32_t selected_lane;
    uint64_t graph_signature64;
    uint64_t tensor_signature64;
    uint64_t decision_signature64;
    char source_identity216[HHS_HASH216_LEN + 1];
    char oracle_identity216[HHS_HASH216_LEN + 1];
    char ethical_text_supervisor_identity216[HHS_HASH216_LEN + 1];
    char training_candidate_hash216[HHS_HASH216_LEN + 1];
    uint8_t accepted;
    uint8_t registry_verified;
    uint8_t specimen_identity_verified;
    uint8_t oracle_verified;
    uint8_t negative_controls_verified;
    uint8_t replay_verified;
    uint8_t ingress_egress_preserved;
    uint8_t natural_language_training;
    uint8_t ethical_text_supervision_required;
    uint8_t ethical_text_supervision_verified;
    uint8_t vm5184_routed;
    uint8_t hash216_candidate_derived;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[6];
} HHSExactPass219Lane5TrainingReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_training_c_abi_version(void);

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_training_method_count(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_training_method(
    uint32_t index,
    HHSExactPass219Lane5TrainingMethodV1 *out_method
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_training_genesis_identity216(
    char out_identity216[HHS_HASH216_LEN + 1]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_training_evaluate_raw(
    const HHSExactPass219Lane5TrainingSpecimenV1 *specimen,
    uint32_t uqcel_profile,
    const uint8_t *delta_be,
    size_t delta_length,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const char previous_hash72[HHS_EXACT_HASH72_STRLEN],
    const char change_hash72[HHS_EXACT_HASH72_STRLEN],
    const char receipt_hash72[HHS_EXACT_HASH72_STRLEN],
    uint8_t use_genesis_transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Lane5TrainingReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
