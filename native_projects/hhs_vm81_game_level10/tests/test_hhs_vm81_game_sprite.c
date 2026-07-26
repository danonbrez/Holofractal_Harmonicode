#include "hhs_vm81_game_sprite.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_sprite_render_is_deterministic_and_projection_only(void) {
    HHSVM81GameRelease release;
    HHSVM81GameRelease before;
    HHSVM81GameSpriteReport first_report;
    HHSVM81GameSpriteReport second_report;
    uint8_t first[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    uint8_t second[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    before = release;
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        first,
        sizeof(first),
        &first_report
    ) == HHS_GAME_STATUS_OK);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
    assert(first_report.state_unchanged == 1U);
    assert(first_report.width == HHS_VM81_GAME_SCREEN_WIDTH);
    assert(first_report.height == HHS_VM81_GAME_SCREEN_HEIGHT);
    assert(first_report.unique_color_buckets >= 64U);
    assert(first_report.nontransparent_pixels == HHS_VM81_GAME_SCREEN_WIDTH * HHS_VM81_GAME_SCREEN_HEIGHT);
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        second,
        sizeof(second),
        &second_report
    ) == HHS_GAME_STATUS_OK);
    assert(memcmp(first, second, sizeof(first)) == 0);
    assert(hhs_hash72_equal(&first_report.frame_hash72, &second_report.frame_hash72));
    assert(hhs_hash216_equal(&first_report.frame_hash216, &second_report.frame_hash216));
}

static void test_gradient_and_overlay_layers_change_pixels(void) {
    HHSVM81GameRelease release;
    HHSVM81GameSpriteReport plain_report;
    HHSVM81GameSpriteReport overlay_report;
    uint8_t plain[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    uint8_t overlay[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    size_t top = 0U;
    size_t lower = ((size_t)80 * HHS_VM81_GAME_SCREEN_WIDTH) * 4U;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(&release, 0U, plain, sizeof(plain), &plain_report) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        overlay,
        sizeof(overlay),
        &overlay_report
    ) == HHS_GAME_STATUS_OK);
    assert(memcmp(plain, overlay, sizeof(plain)) != 0);
    assert(!hhs_hash216_equal(&plain_report.frame_hash216, &overlay_report.frame_hash216));
    assert(plain[top] != plain[lower] || plain[top + 1U] != plain[lower + 1U] || plain[top + 2U] != plain[lower + 2U]);
}

static void test_authoritative_motion_changes_sprite_frame(void) {
    HHSVM81GameRelease release;
    HHSVM81GameSpriteReport before_report;
    HHSVM81GameSpriteReport after_report;
    uint8_t before[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    uint8_t after[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_start(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        before,
        sizeof(before),
        &before_report
    ) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_step(
        &release,
        (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)
    ) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        after,
        sizeof(after),
        &after_report
    ) == HHS_GAME_STATUS_OK);
    assert(memcmp(before, after, sizeof(before)) != 0);
    assert(!hhs_hash72_equal(&before_report.frame_hash72, &after_report.frame_hash72));
    assert(hhs_hash216_equal(&after_report.source_state_hash216, &release.vm.latest_state_identity_hash216));
}

static void test_capacity_and_overlay_validation_fail_closed(void) {
    HHSVM81GameRelease release;
    HHSVM81GameRelease before;
    HHSVM81GameSpriteReport report;
    uint8_t one_pixel[4];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    before = release;
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        one_pixel,
        sizeof(one_pixel),
        &report
    ) == HHS_GAME_STATUS_OUTPUT_CAPACITY);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
    assert(hhs_vm81_game_sprite_render_rgba(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL | (1U << 31),
        one_pixel,
        HHS_VM81_GAME_SPRITE_RGBA_BYTES,
        &report
    ) == HHS_GAME_STATUS_INVALID_OPERAND);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
}

static void test_victory_frame_and_ppm_export(void) {
    HHSVM81GameRelease release;
    HHSVM81GameReleaseReport gameplay_report;
    HHSVM81GameSpriteReport sprite_report;
    FILE* file;
    char header[3];
    const char* path = "dist/test-sprite-victory.ppm";
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_run_headless(&release, &gameplay_report) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_VICTORY);
    assert(hhs_vm81_game_sprite_write_ppm(
        &release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        path,
        &sprite_report
    ) == HHS_GAME_STATUS_OK);
    assert(sprite_report.unique_color_buckets >= 64U);
    file = fopen(path, "rb");
    assert(file != NULL);
    assert(fread(header, 1U, 2U, file) == 2U);
    header[2] = '\0';
    assert(strcmp(header, "P6") == 0);
    assert(fclose(file) == 0);
    assert(remove(path) == 0);
}

int main(void) {
    test_sprite_render_is_deterministic_and_projection_only();
    test_gradient_and_overlay_layers_change_pixels();
    test_authoritative_motion_changes_sprite_frame();
    test_capacity_and_overlay_validation_fail_closed();
    test_victory_frame_and_ppm_export();
    puts("VM81_SPRITE_MAP_OVERLAY_GRADIENTS_VERIFIED");
    return 0;
}
