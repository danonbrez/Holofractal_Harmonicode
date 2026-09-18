#ifndef HHS_PASS219_RLM20_LANE5_INTERNAL_STATE_CLOSURE_1_37_H
#define HHS_PASS219_RLM20_LANE5_INTERNAL_STATE_CLOSURE_1_37_H

#include "hhs_pass219_delta_reciprocal_constructor_1_36.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION UINT32_C(0x00010025)
#define HHS_EXACT_PASS219_RLM20_STAGE UINT32_C(20)

typedef struct HHSExactPass219RLM20Lane5ClosureAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t pass219_specification_contracts;
    uint8_t lane5_implementation_logic;
    uint8_t lane5_inside_rna_cpp_cellular_nucleus_abi;
    uint8_t lane5_outside_pqc_canonical_firewall;
    uint8_t all_state_affecting_runtime_calls_mediated;
    uint8_t environment_independent_vm;
    uint8_t environment_hardware_bytecode_interception_required;
    uint8_t canonical_state_closed_under_hhs_constraints;
    uint8_t successor_preserves_pass219_type_invariants;
    uint8_t four_lane_modality_preserved;
    uint8_t h36_global_compilation_inherited;
    uint8_t rlm20_extends_lane5_kernel;
    uint8_t rlm20_candidate_only;
    uint8_t inherited_equations_unchanged;
    uint8_t inherited_dataflow_unchanged;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t requires_rna_cpp_cell_wall;
    uint8_t requires_lane5_mediation;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[7];
} HHSExactPass219RLM20Lane5ClosureAuthorityV1;

typedef enum HHSExactPass219RLM20Lane5ClosureDecisionV1 {
    HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_INVALID = 0,
    HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_CANDIDATE_READY = 1,
    HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED = 2
} HHSExactPass219RLM20Lane5ClosureDecisionV1;

typedef struct HHSExactPass219RLM20Lane5ClosureReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t pass_number;
    uint32_t learning_stage;
    uint8_t selected_lane;
    uint8_t feedback_lane;
    int8_t feedback_trinary;
    int8_t lo_shu_group;
    uint16_t g243;
    uint16_t reserved0;
    uint64_t request_signature64;
    uint64_t candidate_signature64;
    uint64_t parent_hash216_signature64;
    uint64_t hydration_signature64;
    uint64_t rna_prepared_signature64;
    uint64_t rna_decision_signature64;
    uint64_t lane5_closure_signature64;
    uint64_t lane5_mediation_signature64;
    uint8_t rna_vm5184_routed;
    uint8_t rna_cell_wall_bound;
    uint8_t lane5_mediation_recomputed;
    uint8_t zero_sum_closure_passed;
    uint8_t exact_vm5184_bound;
    uint8_t four_lane_modality_preserved;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_environmental_admission;
    uint8_t environment_hardware_bytecode_intercepted;
    uint8_t reserved1[3];
} HHSExactPass219RLM20Lane5ClosureReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rlm20_lane5_closure_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rlm20_lane5_closure_authority(
    HHSExactPass219RLM20Lane5ClosureAuthorityV1 *out_authority
);

/*
 * Candidate-only runtime preflight.  This is the executable Lane 5 membrane
 * used by the public signed environmental admission seam before PQC/VM81.
 * It intentionally does not inspect host syscalls or hardware bytecode: only
 * the exact HHS VM5184 state and inherited Pass 219 constraints are in scope.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_runtime_preflight(
    uint32_t pass_number,
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219RLM20Lane5ClosureReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
