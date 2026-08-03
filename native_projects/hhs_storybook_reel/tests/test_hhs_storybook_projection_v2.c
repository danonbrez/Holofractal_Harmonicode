#include "hhs_storybook_reel_projection_v2.h"

#include <stdio.h>
#include <string.h>

int main(void) {
    HHSVM81GameRelease release;
    HHSVM81GameRelease before;
    HHSVM81GameTextureReport full_report;
    HHSVM81GameTextureReport reduced_report;
    HHSStorybookProjectionConfigV2 config;
    uint8_t full_rgba[HHS_VM81_TEXTURE_RGBA_BYTES];
    uint8_t reduced_rgba[HHS_VM81_TEXTURE_RGBA_BYTES];
    HHSVM81GameStatus game_status;
    HHSStorybookReelStatus reel_status;

    memset(&release, 0, sizeof(release));
    game_status = hhs_vm81_game_release_init(&release);
    if (game_status != HHS_GAME_STATUS_OK) return 1;
    game_status = hhs_vm81_game_release_start(&release);
    if (game_status != HHS_GAME_STATUS_OK) return 2;
    game_status = hhs_vm81_game_release_step(&release, HHS_VM81_GAME_INPUT_RIGHT);
    if (game_status != HHS_GAME_STATUS_OK) return 3;
    before = release;

    reel_status = hhs_storybook_projection_default_v2(&config);
    if (reel_status != HHS_STORYBOOK_REEL_OK) return 4;
    reel_status = hhs_storybook_projection_set_v2(&config);
    if (reel_status != HHS_STORYBOOK_REEL_OK) return 5;
    game_status = hhs_storybook_texture_render_bridge_v2(
        &release,
        HHS_VM81_TEXTURE_ALL,
        full_rgba,
        sizeof(full_rgba),
        &full_report
    );
    if (game_status != HHS_GAME_STATUS_OK || full_report.state_unchanged == 0U) return 6;
    if (memcmp(&release, &before, sizeof(release)) != 0) return 7;

    config.texture_flags = 0U;
    config.sprite_overlay_flags = 0U;
    reel_status = hhs_storybook_projection_set_v2(&config);
    if (reel_status != HHS_STORYBOOK_REEL_OK) return 8;
    game_status = hhs_storybook_texture_render_bridge_v2(
        &release,
        HHS_VM81_TEXTURE_ALL,
        reduced_rgba,
        sizeof(reduced_rgba),
        &reduced_report
    );
    if (game_status != HHS_GAME_STATUS_OK || reduced_report.state_unchanged == 0U) return 9;
    if (memcmp(&release, &before, sizeof(release)) != 0) return 10;
    if (hhs_hash216_equal(&full_report.frame_hash216, &reduced_report.frame_hash216)) return 11;
    if (full_report.texture_flags != HHS_VM81_TEXTURE_ALL || reduced_report.texture_flags != 0U) return 12;

    config.texture_flags = HHS_VM81_TEXTURE_ALL | (1U << 9);
    if (hhs_storybook_projection_set_v2(&config) != HHS_STORYBOOK_REEL_INVALID_ARGUMENT) return 13;

    puts("HHS_PASS_203_NATIVE_PROJECTION_BRIDGE_VERIFIED");
    return 0;
}
