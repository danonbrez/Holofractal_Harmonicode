#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static HHSExactBigUIntView view_of(const uint8_t *value) {
    HHSExactBigUIntView view;
    memset(&view, 0, sizeof(view));
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

int main(void) {
    HHSExactPass219RLM20Lane5ClosureAuthorityV1 authority;
    HHSExactPass219RLM20Lane5ClosureReceiptV1 first;
    HHSExactPass219RLM20Lane5ClosureReceiptV1 replay;
    HHSExactPass219RLM20Lane5ClosureReceiptV1 rejected;
    HHSExactPass219Hash216TransitionViewV1 parent;
    HHSExactPass219Hash216TransitionViewV1 bad_parent;
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame frame;
    uint8_t P = 4U;
    uint8_t p = 3U;
    uint8_t q = 5U;
    uint8_t delta = 1U;
    uint8_t A = 16U;
    uint8_t B = 16U;
    size_t i;

    CHECK(hhs_exact_pass219_rlm20_lane5_closure_version() ==
          HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION);
    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_rlm20_lane5_closure_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.pass219_specification_contracts == 1U);
    CHECK(authority.lane5_implementation_logic == 1U);
    CHECK(authority.lane5_inside_rna_cpp_cellular_nucleus_abi == 1U);
    CHECK(authority.lane5_outside_pqc_canonical_firewall == 1U);
    CHECK(authority.all_state_affecting_runtime_calls_mediated == 1U);
    CHECK(authority.environment_independent_vm == 1U);
    CHECK(authority.environment_hardware_bytecode_interception_required == 0U);
    CHECK(authority.canonical_state_closed_under_hhs_constraints == 1U);
    CHECK(authority.successor_preserves_pass219_type_invariants == 1U);
    CHECK(authority.four_lane_modality_preserved == 1U);
    CHECK(authority.h36_global_compilation_inherited == 1U);
    CHECK(authority.rlm20_extends_lane5_kernel == 1U);
    CHECK(authority.rlm20_candidate_only == 1U);
    CHECK(authority.inherited_equations_unchanged == 1U);
    CHECK(authority.inherited_dataflow_unchanged == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.pqc_key_authority == 0U);
    CHECK(authority.receipt_clock_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);
    CHECK(authority.requires_rna_cpp_cell_wall == 1U);
    CHECK(authority.requires_lane5_mediation == 1U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    memset(&parent, 0, sizeof(parent));
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) ==
          HHS_EXACT_STATUS_OK);

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = view_of(&P);
    input.p = view_of(&p);
    input.q = view_of(&q);
    input.delta = view_of(&delta);
    input.A = view_of(&A);
    input.B = view_of(&B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    CHECK(hhs_exact_uqcel_source_sha256(input.source_envelope_sha256) ==
          HHS_EXACT_STATUS_OK);
    memcpy(input.previous_hash72, parent.receipt_hash72, HHS_EXACT_HASH72_STRLEN);

    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x0102030405060708) ^ (uint64_t)i;

    memset(&first, 0, sizeof(first));
    CHECK(hhs_exact_pass219_lane5_runtime_preflight(
              220U,
              &input,
              &frame,
              &parent,
              0,
              0U,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              &first) == HHS_EXACT_STATUS_OK);
    CHECK(first.struct_size == sizeof(first));
    CHECK(first.version == HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION);
    CHECK(first.decision == HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_CANDIDATE_READY);
    CHECK(first.learning_stage == HHS_EXACT_PASS219_RLM20_STAGE);
    CHECK(first.selected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    CHECK(first.rna_vm5184_routed == 1U);
    CHECK(first.rna_cell_wall_bound == 1U);
    CHECK(first.lane5_mediation_recomputed == 1U);
    CHECK(first.zero_sum_closure_passed == 1U);
    CHECK(first.exact_vm5184_bound == 1U);
    CHECK(first.four_lane_modality_preserved == 1U);
    CHECK(first.candidate_only == 1U);
    CHECK(first.canonical_mutation_authority == 0U);
    CHECK(first.canonical_hash72_authority == 0U);
    CHECK(first.canonical_hash216_authority == 0U);
    CHECK(first.canonical_persistence_authority == 0U);
    CHECK(first.requires_environmental_admission == 1U);
    CHECK(first.environment_hardware_bytecode_intercepted == 0U);
    CHECK(first.request_signature64 != UINT64_C(0));
    CHECK(first.candidate_signature64 != UINT64_C(0));
    CHECK(first.parent_hash216_signature64 != UINT64_C(0));
    CHECK(first.hydration_signature64 != UINT64_C(0));
    CHECK(first.rna_prepared_signature64 != UINT64_C(0));
    CHECK(first.rna_decision_signature64 != UINT64_C(0));
    CHECK(first.lane5_closure_signature64 != UINT64_C(0));
    CHECK(first.lane5_mediation_signature64 != UINT64_C(0));

    memset(&replay, 0, sizeof(replay));
    CHECK(hhs_exact_pass219_lane5_runtime_preflight(
              220U,
              &input,
              &frame,
              &parent,
              0,
              0U,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              &replay) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&first, &replay, sizeof(first)) == 0);

    memcpy(&bad_parent, &parent, sizeof(bad_parent));
    bad_parent.transition_identity216[0] =
        bad_parent.transition_identity216[0] == '0' ? '1' : '0';
    memset(&rejected, 0, sizeof(rejected));
    CHECK(hhs_exact_pass219_lane5_runtime_preflight(
              220U,
              &input,
              &frame,
              &bad_parent,
              0,
              0U,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              &rejected) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(rejected.decision == HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED);
    CHECK(rejected.canonical_mutation_authority == 0U);
    CHECK(rejected.canonical_hash72_authority == 0U);
    CHECK(rejected.canonical_hash216_authority == 0U);
    CHECK(rejected.canonical_persistence_authority == 0U);
    CHECK(rejected.environment_hardware_bytecode_intercepted == 0U);

    printf("PASS219_RLM20_LANE5_INTERNAL_STATE_CLOSURE_PASS lane=%u mediation=%llu hw_intercept=%u mutation_authority=%u\n",
           (unsigned)first.selected_lane,
           (unsigned long long)first.lane5_mediation_signature64,
           (unsigned)first.environment_hardware_bytecode_intercepted,
           (unsigned)first.canonical_mutation_authority);
    return 0;
}
