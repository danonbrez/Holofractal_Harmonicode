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
#include "hhs_storybook_reel_projection_v2.h"

#define HHS_STORYBOOK_SERIAL_CYCLE_FRAMES 72U
#define HHS_STORYBOOK_SERIAL_DIRECTION_WINDOW 45U

#define hhs_vm81_game_release_step hhs_storybook_reel_serial_step
#define hhs_vm81_game_texture_render_rgba hhs_storybook_texture_render_bridge_v2
#include "hhs_storybook_reel.c"
#undef hhs_vm81_game_texture_render_rgba
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
    uint32_t cycle_frame;
    uint8_t normalized_input;

    if (!release) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->player_frames >= HHS_STORYBOOK_SERIAL_CYCLE_FRAMES) {
        status = hhs_vm81_game_release_restart(release);
        if (status != HHS_GAME_STATUS_OK) return status;
    }

    cycle_frame = release->player_frames % HHS_STORYBOOK_SERIAL_CYCLE_FRAMES;
    normalized_input = (uint8_t)(
        input_bits
        & (uint8_t)~(HHS_VM81_GAME_INPUT_LEFT | HHS_VM81_GAME_INPUT_RIGHT)
    );
    if (((cycle_frame / HHS_STORYBOOK_SERIAL_DIRECTION_WINDOW) & 1U) == 0U) {
        normalized_input = (uint8_t)(normalized_input | HHS_VM81_GAME_INPUT_RIGHT);
    } else {
        normalized_input = (uint8_t)(normalized_input | HHS_VM81_GAME_INPUT_LEFT);
    }

    return hhs_vm81_game_release_step(release, normalized_input);
}
