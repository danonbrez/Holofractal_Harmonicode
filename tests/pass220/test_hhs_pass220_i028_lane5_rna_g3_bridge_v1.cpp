#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace {

void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[
            (i + static_cast<std::size_t>(offset)) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

HHSExactPass220I028Lane5ConstructorWitnessV1 constructor_witness() {
    HHSExactPass220I028Lane5ConstructorWitnessV1 witness{};
    witness.struct_size = static_cast<std::uint32_t>(sizeof(witness));
    witness.version = HHS_EXACT_PASS220_I028_LANE5_G3_VERSION;
    fill_hash72(witness.pipeline_root_hash72, 13U);
    fill_hash72(witness.constructor_graph_root_hash72, 17U);
    witness.green_merged_pr_implementation = 1U;
    witness.green_exact_head_workflow = 1U;
    witness.canonical_contract = 1U;
    witness.canonical_whitepaper_proof = 1U;
    witness.formal_proof_receipt = 1U;
    witness.successful_benchmark_receipt = 1U;
    witness.restart_checkpoint = 1U;
    witness.commit_merge_lineage = 1U;
    witness.registered_repository_service = 1U;
    witness.hash216_validated_composition = 1U;
    return witness;
}

HHSExactVM81Frame frame() {
    HHSExactVM81Frame value{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        value.words[i] = UINT64_C(0x9E3779B97F4A7C15) ^
                         (static_cast<std::uint64_t>(i) *
                          UINT64_C(0x100000001B3));
    }
    value.words[0] = UINT64_C(0x3ff0000000000000);
    value.words[1] = UINT64_C(9);
    value.words[2] = UINT64_C(9);
    return value;
}

}  // namespace

int main() {
    std::uint8_t one = 1U;
    HHSExactUQCELInputV1 input{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = static_cast<std::uint32_t>(sizeof(input.delta));
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;

    HHSExactPass219Hash216TransitionViewV1 transition{};
    assert(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition) ==
           HHS_EXACT_STATUS_OK);

    HHSExactVM81Frame candidate_frame = frame();
    HHSExactPass220I028Lane5ConstructorWitnessV1 witness =
        constructor_witness();
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 result{};

    assert(hhs_exact_pass220_i028_lane5_rna_g3_bridge_version() ==
           HHS_EXACT_PASS220_I028_LANE5_RNA_G3_BRIDGE_VERSION);
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
               &input,
               &candidate_frame,
               &transition,
               &witness,
               0U, 1U, 2U,
               &result) == HHS_EXACT_STATUS_OK);

    assert(result.struct_size == sizeof(result));
    assert(result.surface_linux_api_abi_ingress == 1U);
    assert(result.lane5_zero_bypass_interposer == 1U);
    assert(result.cpp_rna_cell_wall_routed == 1U);
    assert(result.holo4_evidence_equivalent == 1U);
    assert(result.pqc_firewall_required_for_canonical_admission == 1U);
    assert(result.signed_environmental_vm81_required == 1U);
    assert(result.direct_environmental_opcode_canonical_authority == 0U);
    assert(result.direct_abi_canonical_authority == 0U);
    assert(result.direct_vm81_bypass_authority == 0U);
    assert(result.canonical_admission_invoked == 0U);
    assert(result.external_egress_authority == 0U);

    assert(result.g3_candidate.g3_ouroboros_closed == 1U);
    assert(result.g3_candidate.holo4_four_lane_prepared == 1U);
    assert(result.g3_candidate.hash216_self_solving_validation_required == 1U);
    assert(result.g3_candidate.canonical_vm81_mutation_authority == 0U);
    assert(result.g3_candidate.canonical_hash72_authority == 0U);
    assert(result.g3_candidate.canonical_hash216_authority == 0U);
    assert(result.g3_candidate.canonical_persistence_authority == 0U);
    assert(result.rna_prepared.graph_signature64 ==
           result.g3_candidate.holo4_prepared.graph_signature64);
    assert(result.rna_prepared.tensor_signature64 ==
           result.g3_candidate.holo4_prepared.tensor_signature64);
    assert(result.rna_decision.decision_signature64 ==
           result.g3_candidate.holo4_decision.decision_signature64);
    assert(result.rna_decision.selected_lane ==
           result.g3_candidate.holo4_decision.selected_lane);

    HHSExactPass219Hash216TransitionViewV1 forged = transition;
    forged.transition_identity216[0] =
        forged.transition_identity216[0] == '0' ? '1' : '0';
    std::memset(&result, 0xA5, sizeof(result));
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
               &input,
               &candidate_frame,
               &forged,
               &witness,
               0U, 1U, 2U,
               &result) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(result.struct_size == 0U);
    assert(result.canonical_admission_invoked == 0U);

    witness.successful_benchmark_receipt = 0U;
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
               &input,
               &candidate_frame,
               &transition,
               &witness,
               0U, 1U, 2U,
               &result) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    assert(result.canonical_admission_invoked == 0U);

    return 0;
}
