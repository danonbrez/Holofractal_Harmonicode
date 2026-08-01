#include "hhs_pass186_x64_vm81_q144_abi.h"

#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

static HHS186Quantization q(uint16_t g, uint8_t lane, uint8_t row, uint8_t col) {
    HHS186Quantization value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.abi_version = HHS186_ABI_VERSION;
    value.g243 = g;
    value.opcode_lane36 = lane;
    value.root_row12 = row;
    value.root_col12 = col;
    return value;
}

int main(void) {
    HHS186Quantization quant;
    HHS186Quantization decoded;
    HHS186MappingResult result;
    HHS186MappingResult inverse;
    HHS186RegisterImage registers;
    uint32_t expected = 0;
    uint32_t gear;
    uint32_t lane;
    uint32_t row;
    uint32_t col;

    assert(HHS186_Q12 * HHS186_Q12 == HHS186_Q144);
    assert(HHS186_FACTORIAL_Q144_LANES * HHS186_Q144 == HHS186_FACTORIAL_7);
    assert(HHS186_Q144_LANES * HHS186_Q144 == HHS186_VM5184_STATES);
    assert(HHS186_VM81_CELLS * HHS186_VM81_OPERATIONS_PER_CELL == HHS186_VM5184_STATES);
    assert(HHS186_VM5184_STATES * HHS186_G243_CONTROLS == HHS186_HYDRATED_STATES);

    quant = q(0, 0, 0, 0);
    assert(hhs186_x64_vm81_q144_map(11, 13, 17, 19, &quant, &result) == HHS186_STATUS_OK);
    assert(result.instruction_state5184 == 0);
    assert(result.projected_state5184_243 == 0);
    assert(result.vm81_cell == 0);
    assert(result.vm81_operation64 == 0);
    assert(result.ordered_basis == HHS186_BASIS_X);

    quant = q(242, 35, 11, 11);
    assert(hhs186_x64_vm81_q144_map(11, 13, 17, 19, &quant, &result) == HHS186_STATUS_OK);
    assert(result.instruction_state5184 == 5183);
    assert(result.projected_state5184_243 == HHS186_HYDRATED_STATES - 1U);
    assert(result.vm81_cell == 80);
    assert(result.vm81_operation64 == 63);
    assert(result.ordered_basis == HHS186_BASIS_WZ);
    assert(result.operation_class8 == 7);
    assert(result.closure_q144_lane == 1);
    assert(result.factorial_admitted == 0);
    assert(result.q144_index == 143);
    assert(result.u72_pair == 1);
    assert(result.u72_index == 71);

    quant = q(0, 34, 11, 11);
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &quant, &result) == HHS186_STATUS_OK);
    assert(result.instruction_state5184 == 5039);
    assert(result.factorial_admitted == 1);

    quant = q(0, 35, 0, 0);
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &quant, &result) == HHS186_STATUS_OK);
    assert(result.instruction_state5184 == HHS186_FACTORIAL_7);
    assert(result.closure_q144_lane == 1);
    assert(result.factorial_admitted == 0);

    quant = q(0, 0, 0, 4);
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &quant, &result) == HHS186_STATUS_OK);
    assert(result.ordered_basis == HHS186_BASIS_XY);
    assert(result.ordered_tag == UINT16_C(0x5859));
    assert(result.ordered_left == 2 && result.ordered_right == 3);
    assert(result.ordered_product_witness == 6);

    quant = q(0, 0, 0, 5);
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &quant, &inverse) == HHS186_STATUS_OK);
    assert(inverse.ordered_basis == HHS186_BASIS_YX);
    assert(inverse.ordered_tag == UINT16_C(0x5958));
    assert(inverse.ordered_left == 3 && inverse.ordered_right == 2);
    assert(inverse.ordered_product_witness == 6);
    assert(result.ordered_tag != inverse.ordered_tag);

    for (lane = 0; lane < HHS186_Q144_LANES; ++lane) {
        for (row = 0; row < HHS186_Q12; ++row) {
            for (col = 0; col < HHS186_Q12; ++col) {
                for (gear = 0; gear < HHS186_G243_CONTROLS; ++gear) {
                    quant = q((uint16_t)gear, (uint8_t)lane, (uint8_t)row, (uint8_t)col);
                    assert(hhs186_x64_vm81_q144_map(1, 1, 1, 1, &quant, &result) == HHS186_STATUS_OK);
                    assert(result.projected_state5184_243 == expected);
                    assert(hhs186_x64_vm81_q144_unproject(expected, &decoded, &inverse) == HHS186_STATUS_OK);
                    assert(decoded.g243 == quant.g243);
                    assert(decoded.opcode_lane36 == quant.opcode_lane36);
                    assert(decoded.root_row12 == quant.root_row12);
                    assert(decoded.root_col12 == quant.root_col12);
                    assert(inverse.instruction_state5184 == result.instruction_state5184);
                    ++expected;
                }
            }
        }
    }
    assert(expected == HHS186_HYDRATED_STATES);

    memset(&registers, 0, sizeof(registers));
    hhs186_x64_capture_xyzw_registers(11, 13, 17, 19, &registers);
    assert(registers.ingress_rdi_x == 11 && registers.canonical_r8_x == 11);
    assert(registers.ingress_rsi_y == 13 && registers.canonical_r9_y == 13);
    assert(registers.ingress_rdx_z == 17 && registers.canonical_r10_z == 17);
    assert(registers.ingress_rcx_w == 19 && registers.canonical_r11_w == 19);

    printf("HHS_PASS_186_X64_VM81_Q144_ABI_PASS states=%" PRIu32 " max=%" PRIu32 "\n",
           expected, expected - 1U);
    return 0;
}
