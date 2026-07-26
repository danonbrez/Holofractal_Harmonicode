#include "hhs_vm81_game_texture.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_texture_projection_is_deterministic_and_non_mutating(void) {
    HHSVM81GameRelease release;
    HHSVM81GameRelease before;
    HHSVM81GameTextureReport first_report;
    HHSVM81GameTextureReport second_report;
    uint8_t first[HHS_VM81_TEXTURE_RGBA_BYTES];
    uint8_t second[HHS_VM81_TEXTURE_RGBA_BYTES];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    before = release;
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL, first, sizeof(first), &first_report) == HHS_GAME_STATUS_OK);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
    assert(first_report.state_unchanged == 1U);
    assert(first_report.base_projection_unchanged == 1U);
    assert(first_report.unique_color_buckets >= 96U);
    assert(first_report.field_writes > 0U);
    assert(first_report.midground_writes > 0U);
    assert(first_report.material_writes > 0U);
    assert(first_report.semantic_writes > 0U);
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL, second, sizeof(second), &second_report) == HHS_GAME_STATUS_OK);
    assert(memcmp(first, second, sizeof(first)) == 0);
    assert(hhs_hash72_equal(&first_report.frame_hash72, &second_report.frame_hash72));
    assert(hhs_hash216_equal(&first_report.frame_hash216, &second_report.frame_hash216));
}

static void test_inherited_sprite_renderer_is_unchanged(void) {
    HHSVM81GameRelease release;
    HHSVM81GameSpriteReport first_report;
    HHSVM81GameSpriteReport second_report;
    uint8_t first[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    uint8_t second[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(&release, HHS_VM81_SPRITE_OVERLAY_ALL, first, sizeof(first), &first_report) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_sprite_render_rgba(&release, HHS_VM81_SPRITE_OVERLAY_ALL, second, sizeof(second), &second_report) == HHS_GAME_STATUS_OK);
    assert(memcmp(first, second, sizeof(first)) == 0);
    assert(hhs_hash216_equal(&first_report.frame_hash216, &second_report.frame_hash216));
}

static void test_texture_classes_are_independent(void) {
    static const uint32_t flags[5] = {
        HHS_VM81_TEXTURE_FIELD,
        HHS_VM81_TEXTURE_MIDGROUND,
        HHS_VM81_TEXTURE_MATERIALS,
        HHS_VM81_TEXTURE_SEMANTIC,
        HHS_VM81_TEXTURE_PLAYER
    };
    HHSVM81GameRelease release;
    HHSVM81GameTextureReport reports[5];
    uint8_t frames[5][HHS_VM81_TEXTURE_RGBA_BYTES];
    size_t i;
    size_t j;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_start(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_step(&release, (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)) == HHS_GAME_STATUS_OK);
    for (i = 0U; i < 5U; ++i) {
        assert(hhs_vm81_game_texture_render_rgba(&release, flags[i], frames[i], sizeof(frames[i]), &reports[i]) == HHS_GAME_STATUS_OK);
        assert(reports[i].texture_flags == flags[i]);
    }
    assert(reports[0].field_writes > 0U);
    assert(reports[1].midground_writes > 0U);
    assert(reports[2].material_writes > 0U);
    assert(reports[3].semantic_writes > 0U);
    assert(reports[4].player_writes > 0U);
    for (i = 0U; i < 5U; ++i) {
        for (j = i + 1U; j < 5U; ++j) {
            assert(memcmp(frames[i], frames[j], sizeof(frames[i])) != 0);
            assert(!hhs_hash216_equal(&reports[i].frame_hash216, &reports[j].frame_hash216));
        }
    }
}

static void test_motion_changes_texture_projection(void) {
    HHSVM81GameRelease release;
    HHSVM81GameTextureReport before_report;
    HHSVM81GameTextureReport after_report;
    uint8_t before[HHS_VM81_TEXTURE_RGBA_BYTES];
    uint8_t after[HHS_VM81_TEXTURE_RGBA_BYTES];
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_start(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL, before, sizeof(before), &before_report) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_step(&release, (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL, after, sizeof(after), &after_report) == HHS_GAME_STATUS_OK);
    assert(memcmp(before, after, sizeof(before)) != 0);
    assert(!hhs_hash72_equal(&before_report.frame_hash72, &after_report.frame_hash72));
    assert(after_report.player_writes > 0U);
    assert(hhs_hash216_equal(&after_report.source_state_hash216, &release.vm.latest_state_identity_hash216));
}

static void test_fail_closed_and_ppm(void) {
    HHSVM81GameRelease release;
    HHSVM81GameRelease before;
    HHSVM81GameTextureReport report;
    HHSVM81GameReleaseReport gameplay;
    uint8_t one_pixel[4];
    FILE* file;
    char header[3];
    const char* path = "dist/test-texture-victory.ppm";
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    before = release;
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL, one_pixel, sizeof(one_pixel), &report) == HHS_GAME_STATUS_OUTPUT_CAPACITY);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
    assert(hhs_vm81_game_texture_render_rgba(&release, HHS_VM81_TEXTURE_ALL | (1U << 31), one_pixel, HHS_VM81_TEXTURE_RGBA_BYTES, &report) == HHS_GAME_STATUS_INVALID_OPERAND);
    assert(memcmp(&release, &before, sizeof(release)) == 0);
    assert(hhs_vm81_game_release_run_headless(&release, &gameplay) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_texture_write_ppm(&release, HHS_VM81_TEXTURE_ALL, path, &report) == HHS_GAME_STATUS_OK);
    file = fopen(path, "rb");
    assert(file != NULL);
    assert(fread(header, 1U, 2U, file) == 2U);
    header[2] = '\0';
    assert(strcmp(header, "P6") == 0);
    assert(fclose(file) == 0);
    assert(remove(path) == 0);
}

int main(void) {
    test_texture_projection_is_deterministic_and_non_mutating();
    test_inherited_sprite_renderer_is_unchanged();
    test_texture_classes_are_independent();
    test_motion_changes_texture_projection();
    test_fail_closed_and_ppm();
    puts("VM81_GOVERNED_TEXTURE_LAYER_FOUNDATION_VERIFIED");
    return 0;
}
