#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace {

bool same_lane(
    const HHSExactPass219Holo4LaneScoreV1& a,
    const HHSExactPass219Holo4LaneScoreV1& b
) noexcept {
    return a.struct_size == b.struct_size &&
           a.version == b.version &&
           a.lane_id == b.lane_id &&
           a.candidate_only == b.candidate_only &&
           a.exact_integer_only == b.exact_integer_only &&
           a.score == b.score &&
           a.routing_signature64 == b.routing_signature64 &&
           std::memcmp(
               a.cell_contribution,
               b.cell_contribution,
               sizeof(a.cell_contribution)) == 0 &&
           std::memcmp(
               a.bank_contribution,
               b.bank_contribution,
               sizeof(a.bank_contribution)) == 0;
}

bool same_prepared(
    const HHSExactPass219Holo4PreparedV1& a,
    const HHSExactPass219Holo4PreparedV1& b
) noexcept {
    return a.struct_size == b.struct_size &&
           a.version == b.version &&
           a.word_visits == b.word_visits &&
           a.graph_edge_visits == b.graph_edge_visits &&
           a.graph_signature64 == b.graph_signature64 &&
           a.tensor_signature64 == b.tensor_signature64 &&
           a.all_cells_have_20_peers == b.all_cells_have_20_peers &&
           a.reciprocal_phase_closure == b.reciprocal_phase_closure &&
           a.nested_loshu_complete == b.nested_loshu_complete &&
           a.hash216_positions_complete == b.hash216_positions_complete &&
           a.candidate_only == b.candidate_only &&
           a.exact_integer_only == b.exact_integer_only &&
           a.canonical_mutation_authority == b.canonical_mutation_authority &&
           a.canonical_hash72_authority == b.canonical_hash72_authority &&
           a.canonical_hash216_authority == b.canonical_hash216_authority &&
           a.canonical_persistence_authority == b.canonical_persistence_authority &&
           a.floating_point_authority == b.floating_point_authority &&
           std::memcmp(&a.core_features, &b.core_features, sizeof(a.core_features)) == 0 &&
           std::memcmp(&a.core_decision, &b.core_decision, sizeof(a.core_decision)) == 0 &&
           std::memcmp(a.cells, b.cells, sizeof(a.cells)) == 0 &&
           std::memcmp(a.banks, b.banks, sizeof(a.banks)) == 0 &&
           std::memcmp(
               a.source_transition_identity216,
               b.source_transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
}

bool same_decision(
    const HHSExactPass219Holo4DecisionV1& a,
    const HHSExactPass219Holo4DecisionV1& b
) noexcept {
    if (a.struct_size != b.struct_size ||
        a.version != b.version ||
        a.selected_lane != b.selected_lane ||
        a.feedback_lane != b.feedback_lane ||
        a.feedback_trinary != b.feedback_trinary ||
        a.updated != b.updated ||
        a.update_count != b.update_count ||
        a.step_count != b.step_count ||
        a.decision_signature64 != b.decision_signature64 ||
        a.candidate_only != b.candidate_only ||
        a.exact_integer_only != b.exact_integer_only ||
        a.canonical_mutation_authority != b.canonical_mutation_authority ||
        a.canonical_hash72_authority != b.canonical_hash72_authority ||
        a.canonical_hash216_authority != b.canonical_hash216_authority ||
        a.canonical_persistence_authority != b.canonical_persistence_authority ||
        a.floating_point_authority != b.floating_point_authority ||
        std::memcmp(
            a.source_transition_identity216,
            b.source_transition_identity216,
            HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return false;

    for (std::size_t lane = 0U;
         lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
         ++lane) {
        if (!same_lane(a.lanes[lane], b.lanes[lane]))
            return false;
    }
    return true;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass220_i028_lane5_rna_g3_bridge_version(void) {
    return HHS_EXACT_PASS220_I028_LANE5_RNA_G3_BRIDGE_VERSION;
}

extern "C" HHSExactStatus hhs_exact_pass220_i028_lane5_rna_g3_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    uint8_t ieee_cell81,
    uint8_t p4_cell81,
    uint8_t c4_cell81,
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 *out_candidate
) {
    HHSExactPass219Holo4PreparedV1 rna_prepared{};
    HHSExactPass219Holo4DecisionV1 rna_decision{};
    HHSExactPass219Holo4StateV1 g3_state{};
    HHSExactPass220I028Lane5G3CandidateV1 g3_candidate{};

    if (out_candidate != nullptr)
        std::memset(out_candidate, 0, sizeof(*out_candidate));
    if (input == nullptr || frame == nullptr || source_transition == nullptr ||
        constructor_witness == nullptr || out_candidate == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSExactStatus status = hhs_exact_pass219_rna_vm5184_route(
        input,
        frame,
        source_transition,
        HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
        0,
        &rna_prepared,
        &rna_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_holo4_state_init(&g3_state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass220_i028_lane5_g3_candidate(
        frame,
        source_transition,
        &g3_state,
        constructor_witness,
        ieee_cell81,
        p4_cell81,
        c4_cell81,
        &g3_candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (!same_prepared(rna_prepared, g3_candidate.holo4_prepared) ||
        !same_decision(rna_decision, g3_candidate.holo4_decision))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_candidate->struct_size = static_cast<uint32_t>(sizeof(*out_candidate));
    out_candidate->version = HHS_EXACT_PASS220_I028_LANE5_RNA_G3_BRIDGE_VERSION;
    out_candidate->rna_prepared = rna_prepared;
    out_candidate->rna_decision = rna_decision;
    out_candidate->g3_candidate = g3_candidate;
    out_candidate->surface_linux_api_abi_ingress = 1U;
    out_candidate->lane5_zero_bypass_interposer = 1U;
    out_candidate->cpp_rna_cell_wall_routed = 1U;
    out_candidate->holo4_evidence_equivalent = 1U;
    out_candidate->pqc_firewall_required_for_canonical_admission = 1U;
    out_candidate->signed_environmental_vm81_required = 1U;
    out_candidate->direct_environmental_opcode_canonical_authority = 0U;
    out_candidate->direct_abi_canonical_authority = 0U;
    out_candidate->direct_vm81_bypass_authority = 0U;
    out_candidate->canonical_admission_invoked = 0U;
    out_candidate->external_egress_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}
