#include "hhs_pass219_mandatory_genesis_scaling_1_22.hpp"

#include <cassert>
#include <cstdint>
#include <iostream>

int main() {
    using namespace hhs::rna;

    Pass219GenesisQuditView genesis;
    const auto &native = genesis.native();
    assert(native.sudoku_valid == 1U);
    assert(native.trinary_zero_sum_rows == 1U);
    assert(native.trinary_zero_sum_columns == 1U);
    assert(native.trinary_zero_sum_blocks == 1U);
    assert(native.trinary_zero_sum_diagonals == 1U);
    assert(native.hydration_rom_empty_state == 1U);
    assert(native.hydrated_payload_present == 0U);
    assert(genesis.cell(40).cell81 == 40U);

    const auto address = genesis.address(80U, 63U);
    assert(address.linear5184 == 5183U);
    assert(address.hash72_row == 71U);
    assert(address.hash72_column == 71U);

    auto request = make_pass219_data_ml_request(
        HHS_EXACT_PASS219_WORK_ML_INFERENCE,
        17625600ULL,
        1U,
        3U,
        2U
    );
    request.dirty_set_complete = 1U;
    request.dirty_cell_mask[0] = 1U;
    request.dirty_cell_mask[11] = 1U;
    request.dirty_cell_mask[23] = 1U;
    request.dirty_cell_mask[34] = 1U;
    request.dirty_cell_mask[46] = 1U;
    request.dirty_cell_mask[57] = 1U;
    request.dirty_cell_mask[69] = 1U;

    Pass219MandatoryScalingPlan plan(request);
    assert(plan.native().mandatory_for_pass219_data_ml == 1U);
    assert(plan.native().phase_reduction_numerator == 6561ULL);
    assert(plan.native().candidate_realized_lane_units == 10368ULL);
    assert(plan.native().derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_SPARSE);

    HHSExactPass219MandatoryScalingWitnessV1 witness{};
    witness.struct_size = sizeof(witness);
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
    plan.verify(witness);

    std::cout << "PASS219 mandatory Sudoku Genesis scaling C++ conformance: PASS\n";
    return 0;
}
