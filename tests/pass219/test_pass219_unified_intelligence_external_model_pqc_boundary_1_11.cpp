#include "hhs_pass219_unified_intelligence_external_model_pqc_boundary_1_11.hpp"

#include <cassert>
#include <cstdint>

using hhs::rna::ExternalModelResidencyV12;
using hhs::rna::UnifiedIntelligenceCandidateV12;
using hhs::rna::hhs_pass219_unified_intelligence_candidate_valid;

static UnifiedIntelligenceCandidateV12 valid_candidate() {
    UnifiedIntelligenceCandidateV12 candidate{};
    candidate.source_model.digest_present = true;
    candidate.source_model.digest[0] = UINT8_C(0x21);
    candidate.source_model.digest[31] = UINT8_C(0x9f);
    candidate.source_model.immutable_source_archive = true;
    candidate.source_model.residency = ExternalModelResidencyV12::OUTSIDE_PQC_CELL_WALL;
    candidate.source_model.provenance_anchor_inside_pqc = true;
    candidate.source_model.verified_native_projection = true;

    candidate.agi_orchestration_present = true;
    candidate.language_projection_present = true;
    candidate.machine_learning_candidate_present = true;
    candidate.exact_algebraic_solver_present = true;
    candidate.five_lane_hydration_present = true;
    candidate.gpu_latency_candidate_present = true;
    candidate.graphics_geometry_candidate_present = true;
    candidate.realtime_learning_candidate_present = true;
    return candidate;
}

int main() {
    {
        const auto candidate = valid_candidate();
        assert(hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.requests_external_weight_blob_crossing = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.requests_direct_model_commit = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.requests_non_vm81_canonical_commit = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.source_model.provenance_anchor_inside_pqc = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.source_model.verified_native_projection = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.source_model.digest.fill(0U);
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.authority.source_model_blob_is_canonical_state = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.authority.language_model_candidate_only = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.authority.machine_learning_candidate_only = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.authority.gpu_optimizer_candidate_only = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.authority.canonical_hash216_authority_created = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.fifth_lane_authority.canonical_mutation_authority = true;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    {
        auto candidate = valid_candidate();
        candidate.realtime_learning_candidate_present = false;
        assert(!hhs_pass219_unified_intelligence_candidate_valid(candidate));
    }

    return 0;
}
