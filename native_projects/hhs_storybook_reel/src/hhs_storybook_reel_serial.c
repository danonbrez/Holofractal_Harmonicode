/*
 * Storybook-specific serial adapter over the inherited platformer release API.
 *
 * The full platformer playthrough, opcode coverage, receipts, and replay are
 * verified independently by hhs_storybook_verify_full_game_abi(). Final reel
 * projection uses bounded 72-frame VM81 phase cycles so a noninteractive
 * caption reel never inherits an unbounded autonomous gameplay trajectory.
 * This adapter changes no game ABI implementation and creates no competing
 * mutation authority.
 */
#define hhs_vm81_game_release_step hhs_storybook_reel_serial_step
#include "hhs_storybook_reel.c"
#undef hhs_vm81_game_release_step

HHSVM81GameStatus hhs_vm81_game_release_step(
    HHSVM81GameRelease* release,
    uint8_t input_bits
);

HHSVM81GameStatus hhs_storybook_reel_serial_step(
    HHSVM81GameRelease* release,
    uint8_t input_bits
) {
    HHSVM81GameStatus status;
    if (!release) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->player_frames >= 72U) {
        status = hhs_vm81_game_release_restart(release);
        if (status != HHS_GAME_STATUS_OK) return status;
    }
    return hhs_vm81_game_release_step(release, input_bits);
}
