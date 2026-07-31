#include "hhs_storybook_reel.h"
#include "hhs_storybook_reel_style_v2.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static long file_size(const char* path) {
    FILE* file = fopen(path, "rb");
    long size;
    assert(file != NULL);
    assert(fseek(file, 0L, SEEK_END) == 0);
    size = ftell(file);
    assert(fclose(file) == 0);
    return size;
}

static void test_default_geometry_and_scene_plan(void) {
    const char* story = "A small machine woke beneath a copper moon. It crossed the quiet field, found a luminous gate, and carried a forgotten song home.";
    HHSStorybookReelConfig config;
    HHSStorybookScene scenes[HHS_STORYBOOK_REEL_SCENES];
    uint32_t total_frames = 0U;
    uint32_t i;
    assert(hhs_storybook_reel_default_config(&config) == HHS_STORYBOOK_REEL_OK);
    assert(config.fps == 30U);
    assert(config.frame_count == 2700U);
    assert(config.frame_count / config.fps == 90U);
    assert(config.scene_count == 15U);
    assert(hhs_storybook_reel_plan_scenes(story, strlen(story), &config, scenes, HHS_STORYBOOK_REEL_SCENES) == HHS_STORYBOOK_REEL_OK);
    for (i = 0U; i < config.scene_count; ++i) {
        assert(scenes[i].frame_count > 0U);
        assert(strlen(scenes[i].scene_hash72.value) == HHS_HASH72_LEN);
        assert(strlen(scenes[i].scene_hash216.value) == HHS_HASH216_LEN);
        total_frames += scenes[i].frame_count;
    }
    assert(total_frames == config.frame_count);
}

static void test_twelve_tone_reciprocal_palette(void) {
    const char* story = "Twelve colors turn around one reciprocal phase wheel.";
    HHSHash216 story_hash216;
    HHSStorybookReelStyleV2 style;
    HHSStorybookReciprocalPaletteV2 first;
    HHSStorybookReciprocalPaletteV2 repeat;
    HHSStorybookReciprocalPaletteV2 next;
    hhs_hash216_compute(story, strlen(story), &story_hash216);
    assert(hhs_storybook_style_default_v2(&style) == HHS_STORYBOOK_REEL_OK);
    assert(hhs_storybook_reciprocal_palette_v2(&story_hash216, 0U, &style, &first) == HHS_STORYBOOK_REEL_OK);
    assert(hhs_storybook_reciprocal_palette_v2(&story_hash216, 0U, &style, &repeat) == HHS_STORYBOOK_REEL_OK);
    assert(hhs_storybook_reciprocal_palette_v2(&story_hash216, 1U, &style, &next) == HHS_STORYBOOK_REEL_OK);
    assert(memcmp(&first, &repeat, sizeof(first)) == 0);
    assert(first.chromatic_tonic < 12U);
    assert(first.harmony_class < 12U);
    assert(first.phase_x % 6U == 0U);
    assert(first.phase_y % 6U == 0U);
    assert(first.phase_z % 6U == 0U);
    assert(first.phase_w % 6U == 0U);
    assert(first.phase_z == (uint8_t)((first.phase_x + 36U) % 72U));
    assert(strlen(first.palette_hash72.value) == HHS_HASH72_LEN);
    assert(strlen(first.palette_hash216.value) == HHS_HASH216_LEN);
    assert(memcmp(&first.palette_hash216, &next.palette_hash216, sizeof(first.palette_hash216)) != 0);
}

static void test_native_game_render_style_and_replay(void) {
    const char* story = "The lantern keeper followed four phase planes. Red answered teal. Gold answered violet. Every word arrived with the measured pulse of the narration.";
    const char* title = "PHASE LANTERN";
    const char* base_path = "/tmp/hhs-storybook-base.rgba";
    const char* styled_path = "/tmp/hhs-storybook-styled.rgba";
    const char* pcm_path = "/tmp/hhs-storybook-score.pcm";
    HHSStorybookReelConfig config;
    HHSStorybookReelReport render;
    HHSStorybookReelStyleV2 style;
    HHSStorybookStyleReportV2 styled;
    HHSStorybookTimingSpanV2 timings[2];
    size_t story_length = strlen(story);
    long expected_rgba;
    assert(hhs_storybook_reel_default_config(&config) == HHS_STORYBOOK_REEL_OK);
    config.frame_count = 60U;
    config.scene_count = 2U;
    memset(&render, 0, sizeof(render));
    assert(hhs_storybook_reel_render_files(story, story_length, title, strlen(title), &config, base_path, pcm_path, &render) == HHS_STORYBOOK_REEL_OK);
    assert(render.status == HHS_STORYBOOK_REEL_OK);
    assert(render.frame_count == 60U);
    assert(render.duration_seconds == 2U);
    assert(render.opcode_coverage == HHS_STORYBOOK_REEL_FULL_OPCODE_MASK);
    assert(render.replay_verified == 1U);
    assert(render.program_roundtrip_verified == 1U);
    assert(render.state_projection_non_mutating == 1U);
    assert(render.parallel_computation_used == 0U);
    timings[0].index = 0U;
    timings[0].first_frame = 0U;
    timings[0].frame_count = 30U;
    timings[0].text_offset = 0U;
    timings[0].text_length = (uint32_t)(story_length / 2U);
    timings[1].index = 1U;
    timings[1].first_frame = 30U;
    timings[1].frame_count = 30U;
    timings[1].text_offset = timings[0].text_length;
    timings[1].text_length = (uint32_t)(story_length - timings[0].text_length);
    assert(hhs_storybook_style_default_v2(&style) == HHS_STORYBOOK_REEL_OK);
    style.font_face = HHS_STORYBOOK_FONT_BOLD_V2;
    style.font_effect = HHS_STORYBOOK_EFFECT_PHASE_WAVE_V2;
    style.effect_depth = 4U;
    style.effect_amplitude = 5U;
    style.caption_x = 10;
    style.caption_y = 104;
    memset(&styled, 0, sizeof(styled));
    assert(hhs_storybook_style_file_v2(base_path, styled_path, config.frame_count, title, strlen(title), story, story_length, timings, 2U, &style, &styled) == HHS_STORYBOOK_REEL_OK);
    assert(styled.frame_count == 60U);
    assert(styled.timing_span_count == 2U);
    assert(styled.chromatic_tones == 12U);
    assert(styled.reciprocal_phase_offset == 36U);
    assert(styled.font_effect == HHS_STORYBOOK_EFFECT_PHASE_WAVE_V2);
    assert(styled.parallel_computation_used == 0U);
    assert(strlen(styled.styled_frame_chain_hash72.value) == HHS_HASH72_LEN);
    assert(strlen(styled.styled_frame_chain_hash216.value) == HHS_HASH216_LEN);
    expected_rgba = (long)(config.frame_count * HHS_STORYBOOK_REEL_RGBA_BYTES);
    assert(file_size(base_path) == expected_rgba);
    assert(file_size(styled_path) == expected_rgba);
    assert(file_size(pcm_path) == (long)(2U * HHS_STORYBOOK_REEL_AUDIO_RATE * sizeof(int16_t)));
    remove(base_path);
    remove(styled_path);
    remove(pcm_path);
}

static void test_rejections(void) {
    HHSStorybookReelConfig config;
    HHSStorybookScene scenes[HHS_STORYBOOK_REEL_SCENES];
    assert(hhs_storybook_reel_default_config(&config) == HHS_STORYBOOK_REEL_OK);
    assert(hhs_storybook_reel_plan_scenes("", 0U, &config, scenes, HHS_STORYBOOK_REEL_SCENES) == HHS_STORYBOOK_REEL_TEXT_EMPTY);
    config.frame_count = 1U;
    assert(hhs_storybook_reel_plan_scenes("text", 4U, &config, scenes, HHS_STORYBOOK_REEL_SCENES) == HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID);
}

int main(void) {
    test_default_geometry_and_scene_plan();
    test_twelve_tone_reciprocal_palette();
    test_native_game_render_style_and_replay();
    test_rejections();
    puts("HHS_STORYBOOK_REEL_NATIVE_ABI_TESTS_VERIFIED");
    return 0;
}
