#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <cstring>

#if defined(_WIN32)
#define HHS_P219_RNA_VM5184_INTERNAL
#else
#define HHS_P219_RNA_VM5184_INTERNAL __attribute__((visibility("hidden")))
#endif

extern "C" HHS_P219_RNA_VM5184_INTERNAL HHSExactStatus
hhs_pass219_vm81_pqc_route_cpp_cell_wall(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
);

namespace {

void zero_route_outputs(
    HHSExactPass219Holo4PreparedV1 *prepared,
    HHSExactPass219Holo4DecisionV1 *decision
) noexcept {
    if (prepared != nullptr)
        std::memset(prepared, 0, sizeof(*prepared));
    if (decision != nullptr)
        std::memset(decision, 0, sizeof(*decision));
}

bool route_evidence_is_exact_candidate(
    const HHSExactPass219Hash216TransitionViewV1& transition,
    const HHSExactPass219Holo4PreparedV1& prepared,
    const HHSExactPass219Holo4DecisionV1& decision
) noexcept {
    return prepared.struct_size == sizeof(prepared) &&
           prepared.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           decision.struct_size == sizeof(decision) &&
           decision.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           prepared.word_visits == HHS_EXACT_VM81_CELLS &&
           prepared.graph_edge_visits == HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES &&
           prepared.all_cells_have_20_peers == 1U &&
           prepared.reciprocal_phase_closure == 1U &&
           prepared.nested_loshu_complete == 1U &&
           prepared.hash216_positions_complete == 1U &&
           prepared.candidate_only == 1U &&
           prepared.exact_integer_only == 1U &&
           prepared.canonical_mutation_authority == 0U &&
           prepared.canonical_hash72_authority == 0U &&
           prepared.canonical_hash216_authority == 0U &&
           prepared.canonical_persistence_authority == 0U &&
           prepared.floating_point_authority == 0U &&
           decision.selected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT &&
           decision.candidate_only == 1U &&
           decision.exact_integer_only == 1U &&
           decision.canonical_mutation_authority == 0U &&
           decision.canonical_hash72_authority == 0U &&
           decision.canonical_hash216_authority == 0U &&
           decision.canonical_persistence_authority == 0U &&
           decision.floating_point_authority == 0U &&
           std::memcmp(
               prepared.source_transition_identity216,
               transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
           std::memcmp(
               decision.source_transition_identity216,
               transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass219_rna_vm5184_abi_version(void) {
    return HHS_EXACT_PASS219_RNA_VM5184_ABI_VERSION;
}

extern "C" HHSExactStatus hhs_exact_pass219_rna_vm5184_abi_descriptor(
    HHSExactPass219RNAVM5184ABIDescriptorV1 *out_descriptor
) {
    if (out_descriptor == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (hhs_exact_abi_validate() != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    std::memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = static_cast<uint32_t>(sizeof(*out_descriptor));
    out_descriptor->version = HHS_EXACT_PASS219_RNA_VM5184_ABI_VERSION;
    out_descriptor->vm81_cells = HHS_EXACT_VM81_CELLS;
    out_descriptor->vm81_word_bits = HHS_EXACT_VM81_WORD_BITS;
    out_descriptor->vm5184_bits = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->vm5184_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out_descriptor->lane_count = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
    out_descriptor->cpp_rna_cell_wall = 1U;
    out_descriptor->exact_vm5184_carrier = 1U;
    out_descriptor->raw5184_ingress = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    out_descriptor->canonical_mutation_authority = 0U;
    out_descriptor->canonical_hash72_authority = 0U;
    out_descriptor->canonical_hash216_authority = 0U;
    out_descriptor->canonical_persistence_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass219_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};

    zero_route_outputs(out_prepared, out_decision);
    if (input == nullptr || candidate_frame == nullptr || transition == nullptr ||
        out_prepared == nullptr || out_decision == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (feedback_lane != HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE &&
        feedback_lane >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (feedback_trinary < -1 || feedback_trinary > 1)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (hhs_exact_abi_validate() != HHS_EXACT_STATUS_OK ||
        HHS_EXACT_VM81_CELLS * HHS_EXACT_VM81_WORD_BITS != HHS_EXACT_VM81_FRAME_BITS ||
        sizeof(HHSExactVM81Frame) != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(transition) !=
        HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    const HHSExactStatus status = hhs_pass219_vm81_pqc_route_cpp_cell_wall(
        input,
        candidate_frame,
        transition,
        feedback_lane,
        feedback_trinary,
        &prepared,
        &decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!route_evidence_is_exact_candidate(*transition, prepared, decision))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    std::memcpy(out_prepared, &prepared, sizeof(prepared));
    std::memcpy(out_decision, &decision, sizeof(decision));
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass219_rna_raw5184_route(
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    HHSExactVM81Frame frame{};

    zero_route_outputs(out_prepared, out_decision);
    if (input == nullptr || raw_frame_le == nullptr || transition == nullptr ||
        out_prepared == nullptr || out_decision == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (raw_frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    const HHSExactStatus import_status = hhs_exact_vm81_frame_import_le(
        raw_frame_le, raw_frame_length, &frame);
    if (import_status != HHS_EXACT_STATUS_OK)
        return import_status;

    return hhs_exact_pass219_rna_vm5184_route(
        input,
        &frame,
        transition,
        feedback_lane,
        feedback_trinary,
        out_prepared,
        out_decision);
}
