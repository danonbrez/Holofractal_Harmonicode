#include "hhs_pass219_harmonic36_compression_gpu_fabric_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t next64(uint64_t *x) {
    *x ^= *x << 13U;
    *x ^= *x >> 7U;
    *x ^= *x << 17U;
    return *x;
}

static void init_pass210(HHSExactPass219InheritedPass210BindingV1 *p) {
    memset(p, 0, sizeof(*p));
    p->struct_size = sizeof(*p);
    p->version = hhs_exact_pass219_inherited_pass210_version();
    p->pass_number = HHS_EXACT_PASS219_INHERITED_PASS210_NUMBER;
    p->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    p->exact_frame_authority_bound = 1U;
    p->double_witness_coverage_bound = 1U;
    p->single_snapshot_recovery_bound = 1U;
    p->multimodal_agreement_bound = 1U;
    p->strict_compression_domain_bound = 1U;
    p->digest_decode_boundary_bound = 1U;
    p->pass211_successor_bound = 1U;
    p->register_len = 5184U;
    p->snapshot_count = 36U;
    p->snapshot_width = 288U;
    p->snapshot_stride = 144U;
}

static void init_pass207(HHSExactPass219InheritedPass207BindingV1 *p) {
    memset(p, 0, sizeof(*p));
    p->struct_size = sizeof(*p);
    p->version = hhs_exact_pass219_inherited_pass207_version();
    p->pass_number = HHS_EXACT_PASS219_INHERITED_PASS207_NUMBER;
    p->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    p->stable_vm5184_lane_dispatch_bound = 1U;
    p->lane_phase_bijection_bound = 1U;
    p->ordered_cell_pack_bound = 1U;
    p->ordered_hydration_bound = 1U;
    p->exact_cpu_oracle_verification_bound = 1U;
    p->content_keyed_cache_bound = 1U;
    p->stable_vector_ranking_bound = 1U;
    p->candidate_only_bound = 1U;
    p->gpu_hash72_commit_forbidden = 1U;
    p->gpu_canonical_mutation_forbidden = 1U;
    p->gpu_vm81_bypass_forbidden = 1U;
    p->pass205_singleton_vm81_admission_bound = 1U;
    p->physical_gpu_fail_closed = 1U;
    p->pass208_successor_bound = 1U;
    p->logical_lanes_per_batch = 5184U;
}

static void init_pass208(HHSExactPass219InheritedPass208BindingV1 *p) {
    memset(p, 0, sizeof(*p));
    p->struct_size = sizeof(*p);
    p->version = hhs_exact_pass219_inherited_pass208_version();
    p->pass_number = HHS_EXACT_PASS219_INHERITED_PASS208_NUMBER;
    p->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    p->gpu_candidate_expansion_bound = 1U;
    p->exact_cpu_oracle_verification_bound = 1U;
    p->stable_integer_ranking_bound = 1U;
    p->pass205_singleton_vm81_commit_path_bound = 1U;
    p->gpu_hash72_commit_forbidden = 1U;
    p->gpu_canonical_persistence_forbidden = 1U;
    p->gpu_vm81_bypass_forbidden = 1U;
    p->physical_gpu_fail_closed = 1U;
    p->pass209_successor_bound = 1U;
    p->logical_lanes_per_branch = 5184U;
}

int main(void) {
    HHSExactPass219InheritedPass210BindingV1 p210;
    HHSExactPass219InheritedPass207BindingV1 p207;
    HHSExactPass219InheritedPass208BindingV1 p208;
    HHSExactVM81Frame frame;
    HHSExactPass219H36CompressionWitnessV1 cw;
    HHSExactPass219H36GPULocalityPlanV1 plan;
    HHSExactPass219H36GPUEqualityWitnessV1 gw;
    uint64_t seed = UINT64_C(0xA0761D6478BD642F);
    uint32_t i;

    init_pass210(&p210);
    init_pass207(&p207);
    init_pass208(&p208);

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = next64(&seed);

    assert(hhs_exact_pass219_h36_compression_verify(
        &frame, &p210, &cw) == HHS_EXACT_STATUS_OK);
    assert(cw.vm81_boolean_expand_equal == 1U);
    assert(cw.hfc_double_coverage_equal == 1U);
    assert(cw.hfc_all_single_erasure_recoveries_equal == 1U);
    assert(cw.single_snapshot_erasure_drills == 36U);
    assert(cw.fibonacci_descriptor_equal == 1U);
    assert(cw.h36_roundtrip_equal == 1U);
    assert(cw.exact_reconstruction_equal == 1U);

    assert(hhs_exact_pass219_h36_gpu_locality_plan(
        &p207, &p208, 12U, 17U, 3U, 11U, &plan) ==
        HHS_EXACT_STATUS_OK);
    assert(plan.selected_lane_count == 187U);
    assert(plan.avoided_lane_count == 5184U - 187U);
    assert(plan.locality.required_realized_units == 187U);
    assert(plan.candidate_only == 1U);
    assert(plan.exact_cpu_vm81_equality_required == 1U);

    for (i = 0U; i < plan.selected_lane_count; ++i) {
        HHSExactPass219H36FactorizationCircuitV1 c;
        uint32_t word_offset = i / plan.bit_count;
        uint32_t bit_offset = i % plan.bit_count;
        uint32_t expected =
            (plan.first_word144 + word_offset) * 36U +
            (plan.first_bit36 + bit_offset);
        assert(hhs_exact_pass219_h36_gpu_locality_lane(
            &plan, i, &c) == HHS_EXACT_STATUS_OK);
        assert(c.linear5184 == expected);
        assert((uint32_t)c.h36_word144 * 36U + c.h36_bit36 == expected);
        assert((uint32_t)c.vm81_cell81 * 64U + c.vm81_operation64 == expected);
        assert((uint32_t)c.hash72_row72 * 72U + c.hash72_col72 == expected);
    }

    assert(hhs_exact_pass219_h36_gpu_candidate_verify(
        &plan, 187U, &frame, &frame, &gw) == HHS_EXACT_STATUS_OK);
    assert(gw.gpu_cpu_frame_equal == 1U);
    assert(gw.candidate_only_preserved == 1U);
    assert(gw.singleton_vm81_admission_preserved == 1U);

    {
        HHSExactVM81Frame bad = frame;
        bad.words[0] ^= UINT64_C(1);
        assert(hhs_exact_pass219_h36_gpu_candidate_verify(
            &plan, 187U, &bad, &frame, &gw) ==
            HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    {
        HHSExactPass219InheritedPass208BindingV1 bad = p208;
        bad.gpu_vm81_bypass_forbidden = 0U;
        assert(hhs_exact_pass219_h36_gpu_locality_plan(
            &p207, &bad, 0U, 1U, 0U, 1U, &plan) ==
            HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    puts("PASS219 Harmonic36 compression/GPU fabric: PASS");
    return 0;
}
