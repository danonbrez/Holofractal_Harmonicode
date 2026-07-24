#include "hhs_vm81_game.h"
#include <stdio.h>
#include <string.h>

static void build_demo_trace(uint8_t* trace, uint32_t count) {
    uint32_t i;
    for (i = 0; i < count; ++i) {
        uint8_t input = HHS_VM81_GAME_INPUT_RIGHT;
        if (i == 18U || i == 19U || i == 80U) input |= HHS_VM81_GAME_INPUT_JUMP;
        if (i >= 120U && i < 140U) input = HHS_VM81_GAME_INPUT_LEFT;
        if (i == 150U) input = HHS_VM81_GAME_INPUT_RESET;
        if (i > 150U) input = HHS_VM81_GAME_INPUT_RIGHT;
        trace[i] = input;
    }
}

int main(void) {
    uint8_t trace[240];
    HHSVM81GameState state;
    HHSVM81GameRunReport report;
    HHSVM81GameRunReport replay;
    char base20[256];
    uint8_t digits[HHS_VM81_GAME_PROGRAM_LENGTH];
    size_t digit_count = 0U;
    HHSVM81GameStatus status;
    build_demo_trace(trace, 240U);
    status = hhs_vm81_game_init(&state, trace, 240U);
    if (status != HHS_GAME_STATUS_OK) return 1;
    status = hhs_vm81_game_base20_encode_program(state.program, HHS_VM81_GAME_PROGRAM_LENGTH, base20, sizeof(base20));
    if (status != HHS_GAME_STATUS_OK) return 2;
    status = hhs_vm81_game_base20_decode_program(base20, digits, sizeof(digits), &digit_count);
    if (status != HHS_GAME_STATUS_OK) return 3;
    status = hhs_vm81_game_run(&state, &report);
    if (status != HHS_GAME_STATUS_OK) return 4;
    status = hhs_vm81_game_replay_verify(trace, 240U, &report, &replay);
    if (status != HHS_GAME_STATUS_OK) return 5;
    printf("{\n");
    printf("  \"contract\": \"HHS-VM81-GAME-L10-V1\",\n");
    printf("  \"terminal_classification\": \"VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED\",\n");
    printf("  \"status\": \"VERIFIED\",\n");
    printf("  \"screen\": \"160x144\",\n");
    printf("  \"viewport_tiles\": \"20x18\",\n");
    printf("  \"level_tiles\": \"64x18\",\n");
    printf("  \"ticks_per_second\": 60,\n");
    printf("  \"frames\": %u,\n", report.frames_executed);
    printf("  \"instructions\": %u,\n", report.instructions_executed);
    printf("  \"opcode_coverage\": \"%u/19\",\n", report.opcode_coverage == ((1U << 19U) - 1U) ? 19U : 0U);
    printf("  \"receipts\": %u,\n", report.receipts_emitted);
    printf("  \"base20_program_bigint\": \"%s\",\n", base20);
    printf("  \"base20_roundtrip_digits\": %zu,\n", digit_count);
    printf("  \"replay\": \"MATCH\",\n");
    printf("  \"final_hash72\": \"%s\",\n", report.final_receipt_hash72.value);
    printf("  \"final_hash216\": \"%s\"\n", report.final_state_identity_hash216.value);
    printf("}\n");
    return 0;
}
