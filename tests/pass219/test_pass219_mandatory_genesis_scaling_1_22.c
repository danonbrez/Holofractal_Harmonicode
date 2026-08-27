#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static HHSExactPass219MandatoryScalingRequestV1 make_request(uint32_t work_kind) {
    HHSExactPass219MandatoryScalingRequestV1 request;
    uint32_t i;
    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.version = hhs_exact_pass219_mandatory_genesis_scaling_version();
    request.work_kind = work_kind;
    request.phase_depth = 2U;
    request.source_count = 17625600ULL;
    request.candidate_family_count = 2U;
    request.phase_selected_s[0] = 1U;
    request.phase_selected_s[1] = 1U;
    request.projection_numerator_p = 1U;
    request.projection_denominator_q = 3U;
    request.exact_phase_selector_available = 1U;
    request.dirty_set_complete = 1U;
    for (i = 0U; i < 7U; ++i)
        request.dirty_cell_mask[(i * 81U) / 7U] = 1U;
    return request;
}

int main(void) {
    HHSExactPass219GenesisDescriptorV1 genesis;
    uint32_t trit_counts[3] = {0U, 0U, 0U};
    uint32_t loshu_counts[10] = {0U};
    uint32_t phase_counts[9] = {0U};
    uint32_t cell;
    uint32_t operation;
    uint32_t work_kind;

    assert(hhs_exact_pass219_mandatory_genesis_scaling_version() ==
           ((1U << 16U) | (22U << 8U)));

    assert(hhs_exact_pass219_genesis_descriptor(&genesis) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_genesis_validate(&genesis) == HHS_EXACT_STATUS_OK);
    assert(genesis.cell_count == 81U);
    assert(genesis.address_count == 5184U);
    assert(genesis.sudoku_valid == 1U);
    assert(genesis.trinary_zero_sum_rows == 1U);
    assert(genesis.trinary_zero_sum_columns == 1U);
    assert(genesis.trinary_zero_sum_blocks == 1U);
    assert(genesis.trinary_zero_sum_diagonals == 1U);
    assert(genesis.lo_shu_binding_valid == 1U);
    assert(genesis.phase_channel_binding_valid == 1U);
    assert(genesis.hydration_rom_empty_state == 1U);
    assert(genesis.addressable_geometry_initialized == 1U);
    assert(genesis.hydrated_payload_present == 0U);
    assert(genesis.canonical_pass219_data_plane == 1U);

    for (cell = 0U; cell < 81U; ++cell) {
        const HHSExactPass219GenesisCellV1 *record = &genesis.cells[cell];
        assert(record->cell81 == cell);
        assert(record->row9 == cell / 9U);
        assert(record->column9 == cell % 9U);
        assert(record->sudoku_symbol9 < 9U);
        assert(record->trit >= -1 && record->trit <= 1);
        ++trit_counts[(uint32_t)(record->trit + 1)];
        assert(record->lo_shu_value >= 1U && record->lo_shu_value <= 9U);
        ++loshu_counts[record->lo_shu_value];
        assert(record->phase_channel < 9U);
        ++phase_counts[record->phase_channel];
    }

    assert(trit_counts[0] == 27U);
    assert(trit_counts[1] == 27U);
    assert(trit_counts[2] == 27U);
    for (cell = 1U; cell <= 9U; ++cell)
        assert(loshu_counts[cell] == 9U);
    for (cell = 0U; cell < 9U; ++cell)
        assert(phase_counts[cell] == 9U);

    for (cell = 0U; cell < 81U; ++cell) {
        for (operation = 0U; operation < 64U; ++operation) {
            HHSExactPass219GenesisAddressV1 encoded;
            HHSExactPass219GenesisAddressV1 decoded;
            const uint16_t linear = (uint16_t)(cell * 64U + operation);
            assert(hhs_exact_pass219_genesis_address_encode(
                       (uint8_t)cell, (uint8_t)operation, &encoded) == HHS_EXACT_STATUS_OK);
            assert(hhs_exact_pass219_genesis_address_decode(
                       linear, &decoded) == HHS_EXACT_STATUS_OK);
            assert(memcmp(&encoded, &decoded, sizeof(encoded)) == 0);
            assert(encoded.linear5184 == linear);
            assert(encoded.phase_alpha8 == operation / 8U);
            assert(encoded.phase_beta8 == operation % 8U);
            assert(encoded.hash72_row == linear / 72U);
            assert(encoded.hash72_column == linear % 72U);
        }
    }

    {
        HHSExactPass219GenesisDescriptorV1 tampered = genesis;
        tampered.cells[40].trit =
            (int8_t)(tampered.cells[40].trit == 1 ? -1 : 1);
        assert(hhs_exact_pass219_genesis_validate(&tampered) ==
               HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    for (work_kind = HHS_EXACT_PASS219_WORK_DATA_INGEST;
         work_kind <= HHS_EXACT_PASS219_WORK_REPLAY;
         ++work_kind) {
        HHSExactPass219MandatoryScalingRequestV1 request = make_request(work_kind);
        HHSExactPass219MandatoryScalingPlanV1 plan;
        HHSExactPass219MandatoryScalingWitnessV1 witness;

        assert(hhs_exact_pass219_mandatory_scaling_plan(&request, &plan) ==
               HHS_EXACT_STATUS_OK);
        assert(plan.work_kind == work_kind);
        assert(plan.mandatory_for_pass219_data_ml == 1U);
        assert(plan.stage_count == 9U);
        assert(plan.stage_order[0] == HHS_EXACT_PASS219_STAGE_GENESIS_NORMALIZE);
        assert(plan.stage_order[1] == HHS_EXACT_PASS219_STAGE_PHASE_LOCALITY);
        assert(plan.stage_order[2] == HHS_EXACT_PASS219_STAGE_PASS207_BATCH_CACHE);
        assert(plan.stage_order[3] == HHS_EXACT_PASS219_STAGE_PASS208_CANDIDATE_EXPANSION);
        assert(plan.stage_order[4] == HHS_EXACT_PASS219_STAGE_EXACT_CPU_VM_ORACLE);
        assert(plan.stage_order[5] == HHS_EXACT_PASS219_STAGE_SINGLETON_VM81_ADMISSION);
        assert(plan.stage_order[6] == HHS_EXACT_PASS219_STAGE_I7_SELECTIVE_PROJECTION);
        assert(plan.stage_order[7] == HHS_EXACT_PASS219_STAGE_I8_SPARSE_DIRTY_DERIVED);
        assert(plan.stage_order[8] == HHS_EXACT_PASS219_STAGE_HASH72_HASH216_EXISTING_PATH);
        assert(plan.potential_phase_volume == 6561ULL);
        assert(plan.materialized_phase_volume == 1ULL);
        assert(plan.phase_reduction_numerator == 6561ULL);
        assert(plan.phase_reduction_denominator == 1ULL);
        assert(plan.candidate_base_lane_units == 10368ULL);
        assert(plan.candidate_realized_lane_units == 10368ULL);
        assert(plan.selected_projection_count == 5875200ULL);
        assert(plan.projection_avoided_count == 11750400ULL);
        assert(plan.derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_SPARSE);
        assert(plan.sparse_update_count > 0U);
        assert(plan.sparse_update_count < plan.selected_projection_count);
        assert(plan.sparse_update_count + plan.sparse_avoided_selected_count ==
               plan.selected_projection_count);
        assert(plan.canonical_mutation_authority == 0U);
        assert(plan.canonical_persistence_authority == 0U);
        assert(plan.canonical_hash72_authority == 0U);
        assert(plan.floating_point_authority == 0U);

        memset(&witness, 0, sizeof(witness));
        witness.struct_size = (uint32_t)sizeof(witness);
        witness.version = hhs_exact_pass219_mandatory_genesis_scaling_version();
        witness.genesis_validated = 1U;
        witness.original_identity_preserved = 1U;
        witness.pass207_deterministic_integer_only = 1U;
        witness.pass207_stable_lane_identity = 1U;
        witness.pass208_candidate_only = 1U;
        witness.exact_cpu_vm_oracle_equal = 1U;
        witness.singleton_vm81_admission_preserved = 1U;
        witness.selective_projection_exact_equal = 1U;
        witness.dirty_set_complete = 1U;
        witness.sparse_projection_exact_equal = 1U;
        witness.hash72_hash216_authority_preserved = 1U;
        assert(hhs_exact_pass219_mandatory_scaling_verify(&plan, &witness) ==
               HHS_EXACT_STATUS_OK);

        witness.exact_cpu_vm_oracle_equal = 0U;
        assert(hhs_exact_pass219_mandatory_scaling_verify(&plan, &witness) ==
               HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    {
        HHSExactPass219MandatoryScalingRequestV1 request =
            make_request(HHS_EXACT_PASS219_WORK_ML_TRAIN);
        HHSExactPass219MandatoryScalingPlanV1 plan;
        request.exact_phase_selector_available = 0U;
        assert(hhs_exact_pass219_mandatory_scaling_plan(&request, &plan) ==
               HHS_EXACT_STATUS_OK);
        assert(plan.phase_route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_DENSE_REQUIRED);
        assert(plan.candidate_realized_lane_units == 10368ULL * 6561ULL);
    }

    {
        HHSExactPass219MandatoryScalingRequestV1 request =
            make_request(HHS_EXACT_PASS219_WORK_ML_INFERENCE);
        HHSExactPass219MandatoryScalingPlanV1 plan;
        request.dirty_set_complete = 0U;
        assert(hhs_exact_pass219_mandatory_scaling_plan(&request, &plan) ==
               HHS_EXACT_STATUS_OK);
        assert(plan.derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_FULL);
        assert(plan.sparse_update_count == plan.selected_projection_count);
        assert(plan.sparse_avoided_selected_count == 0U);
    }

    {
        HHSExactPass219MandatoryScalingRequestV1 request =
            make_request(HHS_EXACT_PASS219_WORK_DATA_TRANSFORM);
        HHSExactPass219MandatoryScalingPlanV1 plan;
        request.canonical_authority_requested = 1U;
        assert(hhs_exact_pass219_mandatory_scaling_plan(&request, &plan) ==
               HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    {
        HHSExactPass219MandatoryScalingRequestV1 request =
            make_request(HHS_EXACT_PASS219_WORK_FEATURE_HYDRATION);
        HHSExactPass219MandatoryScalingPlanV1 plan;
        uint32_t i;
        request.phase_depth = 9U;
        memset(request.phase_selected_s, 0, sizeof(request.phase_selected_s));
        for (i = 0U; i < 9U; ++i)
            request.phase_selected_s[i] = 1U;
        assert(hhs_exact_pass219_mandatory_scaling_plan(&request, &plan) ==
               HHS_EXACT_STATUS_OK);
        assert(plan.potential_phase_volume == 150094635296999121ULL);
        assert(plan.materialized_phase_volume == 1ULL);
        assert(plan.candidate_realized_lane_units == 10368ULL);
    }

    puts("PASS219 mandatory Sudoku Genesis scaling C conformance: PASS");
    return 0;
}
