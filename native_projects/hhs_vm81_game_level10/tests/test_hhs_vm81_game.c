#include "hhs_vm81_game.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void trace_build(uint8_t* trace, uint32_t count) {
    uint32_t i;
    for (i = 0; i < count; ++i) {
        trace[i] = HHS_VM81_GAME_INPUT_RIGHT;
        if (i == 10U || i == 11U || i == 72U) trace[i] |= HHS_VM81_GAME_INPUT_JUMP;
        if (i >= 100U && i < 110U) trace[i] = HHS_VM81_GAME_INPUT_LEFT;
        if (i == 130U) trace[i] = HHS_VM81_GAME_INPUT_RESET;
    }
}

static void test_contract_constants(void) {
    assert(HHS_VM81_GAME_SCREEN_WIDTH == 160);
    assert(HHS_VM81_GAME_SCREEN_HEIGHT == 144);
    assert(HHS_VM81_GAME_TILE_SIZE == 8);
    assert(HHS_VM81_GAME_VIEW_TILES_X == 20);
    assert(HHS_VM81_GAME_VIEW_TILES_Y == 18);
    assert(HHS_VM81_GAME_LEVEL_TILES_X == 64);
    assert(HHS_VM81_GAME_LEVEL_TILES_Y == 18);
    assert(HHS_VM81_GAME_PLAYER_WIDTH == 16);
    assert(HHS_VM81_GAME_PLAYER_HEIGHT == 16);
    assert(HHS_VM81_GAME_TICKS_PER_SECOND == 60);
    assert(HHS_VM81_GAME_PROGRAM_LENGTH == 19);
    assert(HHS_VM81_GAME_BASE20_TERMINATOR == 19);
}

static void test_opcode_registry(void) {
    const uint8_t expected[19] = {7,1,12,14,20,21,18,19,15,16,13,3,4,17,2,6,5,9,22};
    uint32_t i;
    for (i = 0; i < 19U; ++i) {
        assert(strcmp(hhs_vm81_game_opcode_name((uint8_t)i), "INVALID") != 0);
        assert(hhs_vm81_game_registered_opcode((uint8_t)i) == expected[i]);
    }
    assert(hhs_vm81_game_registered_opcode(19U) == 0xffU);
}

static void test_base20_roundtrip(void) {
    uint8_t trace[1] = {0U};
    HHSVM81GameState state;
    char decimal[256];
    uint8_t digits[19];
    size_t count = 0U;
    uint32_t i;
    assert(hhs_vm81_game_init(&state, trace, 1U) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_base20_encode_program(state.program, 19U, decimal, sizeof(decimal)) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_base20_decode_program(decimal, digits, sizeof(digits), &count) == HHS_GAME_STATUS_OK);
    assert(count == 19U);
    for (i = 0; i < 19U; ++i) assert(digits[i] == i);
    assert(hhs_vm81_game_base20_decode_program("19", digits, sizeof(digits), &count) == HHS_GAME_STATUS_BASE20_INVALID);
}

static void test_execution_and_replay(void) {
    uint8_t trace[180];
    HHSVM81GameState state;
    HHSVM81GameRunReport report;
    HHSVM81GameRunReport replay;
    trace_build(trace, 180U);
    assert(hhs_vm81_game_init(&state, trace, 180U) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_run(&state, &report) == HHS_GAME_STATUS_OK);
    assert(state.halted == 1U);
    assert(report.frames_executed == 180U);
    assert(report.opcode_coverage == ((1U << 19U) - 1U));
    assert(report.instructions_executed >= 17U * 180U);
    assert(report.receipts_emitted == report.instructions_executed);
    assert(report.final_player.x_subpx >= 0);
    assert(report.final_player.y_subpx >= 0);
    assert(report.final_camera_x_px <= 352U);
    assert(report.final_player.animation_state <= HHS_GAME_ANIM_FALL);
    assert(hhs_vm81_game_replay_verify(trace, 180U, &report, &replay) == HHS_GAME_STATUS_OK);
    assert(hhs_hash72_equal(&report.final_receipt_hash72, &replay.final_receipt_hash72));
    assert(hhs_hash216_equal(&report.final_state_identity_hash216, &replay.final_state_identity_hash216));
}

static void test_fail_closed_requests(void) {
    uint8_t trace[4] = {0U, 0U, 0U, 0U};
    HHSVM81GameState state;
    HHSVM81GameState before;
    HHSVM81GameRequest request;
    HHSVM81GameResult result;
    assert(hhs_vm81_game_init(&state, trace, 4U) == HHS_GAME_STATUS_OK);
    before = state;
    memset(&request, 0, sizeof(request));
    request.struct_size = sizeof(request);
    request.abi_version = HHS_VM81_GAME_ABI_VERSION;
    request.authority_admission = HHS_VM81_GAME_AUTHORITY_REJECTED;
    request.expected_generation = state.generation;
    request.expected_step = state.step;
    request.instruction = state.program[state.pc];
    assert(hhs_vm81_game_execute(&state, &request, &result) == HHS_GAME_STATUS_AUTHORITY_REJECTED);
    assert(memcmp(&state, &before, sizeof(state)) == 0);

    request.authority_admission = HHS_VM81_GAME_AUTHORITY_ADMITTED;
    request.expected_generation++;
    assert(hhs_vm81_game_execute(&state, &request, &result) == HHS_GAME_STATUS_STALE_GENERATION);
    assert(memcmp(&state, &before, sizeof(state)) == 0);

    request.expected_generation = state.generation;
    request.expected_step++;
    assert(hhs_vm81_game_execute(&state, &request, &result) == HHS_GAME_STATUS_STALE_STEP);
    assert(memcmp(&state, &before, sizeof(state)) == 0);

    request.expected_step = state.step;
    request.instruction.opcode_digit = 99U;
    assert(hhs_vm81_game_execute(&state, &request, &result) == HHS_GAME_STATUS_INVALID_OPCODE);
    assert(memcmp(&state, &before, sizeof(state)) == 0);

    request.instruction = state.program[state.pc];
    request.instruction.a = 1;
    assert(hhs_vm81_game_execute(&state, &request, &result) == HHS_GAME_STATUS_INVALID_OPERAND);
    assert(memcmp(&state, &before, sizeof(state)) == 0);
}

static void test_loshu_and_closure(void) {
    uint8_t trace[2] = {HHS_VM81_GAME_INPUT_RIGHT, 0U};
    HHSVM81GameState state;
    static const uint8_t lo_shu[9] = {4,9,2,3,5,7,8,1,6};
    uint32_t i;
    assert(hhs_vm81_game_init(&state, trace, 2U) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_validate_state(&state));
    for (i = 0; i < 9U; ++i) assert(state.vm81[72U + i] == lo_shu[i]);
    assert(((state.xyzw[0] + state.xyzw[1] - state.xyzw[2] - state.xyzw[3]) % 72) == 0);
}

int main(void) {
    test_contract_constants();
    test_opcode_registry();
    test_base20_roundtrip();
    test_execution_and_replay();
    test_fail_closed_requests();
    test_loshu_and_closure();
    puts("VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED");
    return 0;
}
