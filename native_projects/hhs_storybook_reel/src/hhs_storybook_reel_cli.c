#include "hhs_storybook_reel.h"
#include "hhs_storybook_reel_style_v2.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char* hhs_argument_value(int argc, char** argv, const char* name) {
    int i;
    for (i = 1; i + 1 < argc; ++i) {
        if (strcmp(argv[i], name) == 0) return argv[i + 1];
    }
    return NULL;
}

static unsigned long hhs_parse_unsigned(const char* value, unsigned long fallback) {
    char* end = NULL;
    unsigned long parsed;
    if (!value || *value == '\0') return fallback;
    errno = 0;
    parsed = strtoul(value, &end, 10);
    if (errno != 0 || !end || *end != '\0') return fallback;
    return parsed;
}

static long hhs_parse_signed(const char* value, long fallback) {
    char* end = NULL;
    long parsed;
    if (!value || *value == '\0') return fallback;
    errno = 0;
    parsed = strtol(value, &end, 10);
    if (errno != 0 || !end || *end != '\0') return fallback;
    return parsed;
}

static char* hhs_read_text(const char* path, size_t* out_length) {
    FILE* file;
    long size;
    size_t read_count;
    char* buffer;
    if (!path || !out_length) return NULL;
    file = fopen(path, "rb");
    if (!file) return NULL;
    if (fseek(file, 0L, SEEK_END) != 0) { fclose(file); return NULL; }
    size = ftell(file);
    if (size < 0L || (unsigned long)size > HHS_STORYBOOK_REEL_MAX_TEXT_BYTES) { fclose(file); return NULL; }
    if (fseek(file, 0L, SEEK_SET) != 0) { fclose(file); return NULL; }
    buffer = (char*)malloc((size_t)size + 1U);
    if (!buffer) { fclose(file); return NULL; }
    read_count = fread(buffer, 1U, (size_t)size, file);
    if (read_count != (size_t)size || fclose(file) != 0) { free(buffer); return NULL; }
    buffer[read_count] = '\0';
    *out_length = read_count;
    return buffer;
}

static int hhs_read_timings(
    const char* path,
    HHSStorybookTimingSpanV2* timings,
    size_t capacity,
    size_t* out_count
) {
    FILE* file;
    size_t count = 0U;
    unsigned int index;
    unsigned int first_frame;
    unsigned int frame_count;
    unsigned int text_offset;
    unsigned int text_length;
    if (!path || !timings || !out_count) return 0;
    file = fopen(path, "rb");
    if (!file) return 0;
    while (count < capacity) {
        int scanned = fscanf(file, "%u %u %u %u %u", &index, &first_frame, &frame_count, &text_offset, &text_length);
        if (scanned == EOF) break;
        if (scanned != 5 || frame_count == 0U) { fclose(file); return 0; }
        timings[count].index = index;
        timings[count].first_frame = first_frame;
        timings[count].frame_count = frame_count;
        timings[count].text_offset = text_offset;
        timings[count].text_length = text_length;
        count++;
    }
    if (fclose(file) != 0 || count == 0U) return 0;
    *out_count = count;
    return 1;
}

static int hhs_default_timings(
    const char* text,
    size_t text_length,
    const HHSStorybookReelConfig* config,
    HHSStorybookTimingSpanV2* timings,
    size_t capacity,
    size_t* out_count
) {
    HHSStorybookScene scenes[HHS_STORYBOOK_REEL_SCENES];
    uint32_t i;
    HHSStorybookReelStatus status;
    if (capacity < config->scene_count) return 0;
    status = hhs_storybook_reel_plan_scenes(text, text_length, config, scenes, HHS_STORYBOOK_REEL_SCENES);
    if (status != HHS_STORYBOOK_REEL_OK) return 0;
    for (i = 0U; i < config->scene_count; ++i) {
        timings[i].index = scenes[i].index;
        timings[i].first_frame = scenes[i].first_frame;
        timings[i].frame_count = scenes[i].frame_count;
        timings[i].text_offset = scenes[i].text_offset;
        timings[i].text_length = scenes[i].text_length;
    }
    *out_count = config->scene_count;
    return 1;
}

static int hhs_write_manifest(
    const char* path,
    const HHSStorybookReelReport* render,
    const HHSStorybookStyleReportV2* style,
    const HHSStorybookReelConfig* config,
    size_t timing_count
) {
    FILE* file = fopen(path, "wb");
    if (!file) return 0;
    fprintf(file,
        "{\n"
        "  \"schema\": \"HHS_STORYBOOK_REEL_NATIVE_MANIFEST_V2\",\n"
        "  \"classification\": \"%s\",\n"
        "  \"status\": \"%s\",\n"
        "  \"status_code\": %u,\n"
        "  \"width\": %u,\n"
        "  \"height\": %u,\n"
        "  \"fps\": %u,\n"
        "  \"frame_count\": %u,\n"
        "  \"duration_seconds\": %u,\n"
        "  \"timing_span_count\": %u,\n"
        "  \"audio_rate\": %u,\n"
        "  \"audio_samples\": %u,\n"
        "  \"game_steps\": %u,\n"
        "  \"opcode_coverage\": \"%u/19\",\n"
        "  \"receipts_emitted\": %u,\n"
        "  \"replay_verified\": %s,\n"
        "  \"program_roundtrip_verified\": %s,\n"
        "  \"state_projection_non_mutating\": %s,\n"
        "  \"parallel_computation_used\": false,\n"
        "  \"chromatic_tones\": %u,\n"
        "  \"reciprocal_phase_offset\": %u,\n"
        "  \"font_face\": %u,\n"
        "  \"font_effect\": %u,\n"
        "  \"font_scale\": %u,\n"
        "  \"palette_mode\": %u,\n"
        "  \"story_hash72\": \"%s\",\n"
        "  \"story_hash216\": \"%s\",\n"
        "  \"frame_chain_hash72\": \"%s\",\n"
        "  \"frame_chain_hash216\": \"%s\",\n"
        "  \"styled_frame_chain_hash72\": \"%s\",\n"
        "  \"styled_frame_chain_hash216\": \"%s\",\n"
        "  \"palette_chain_hash72\": \"%s\",\n"
        "  \"palette_chain_hash216\": \"%s\",\n"
        "  \"timing_hash72\": \"%s\",\n"
        "  \"timing_hash216\": \"%s\",\n"
        "  \"final_game_receipt_hash72\": \"%s\",\n"
        "  \"final_game_state_hash216\": \"%s\",\n"
        "  \"ffmpeg_required_only_for_mp4_and_audio_codec_transport\": true\n"
        "}\n",
        config->fps == HHS_STORYBOOK_REEL_FPS && config->frame_count == HHS_STORYBOOK_REEL_FRAME_COUNT
            ? "HHS_90_SECOND_STORYBOOK_REEL_NATIVE_ABI_VERIFIED"
            : "HHS_STORYBOOK_REEL_DIAGNOSTIC_NATIVE_ABI_VERIFIED",
        hhs_storybook_reel_status_name((HHSStorybookReelStatus)render->status),
        render->status,
        render->width,
        render->height,
        render->fps,
        render->frame_count,
        render->duration_seconds,
        (unsigned int)timing_count,
        render->audio_rate,
        render->audio_samples,
        render->game_steps,
        render->opcode_coverage == HHS_STORYBOOK_REEL_FULL_OPCODE_MASK ? 19U : 0U,
        render->receipts_emitted,
        render->replay_verified ? "true" : "false",
        render->program_roundtrip_verified ? "true" : "false",
        render->state_projection_non_mutating ? "true" : "false",
        style->chromatic_tones,
        style->reciprocal_phase_offset,
        style->font_face,
        style->font_effect,
        style->font_scale,
        style->palette_mode,
        render->story_hash72.value,
        render->story_hash216.value,
        render->frame_chain_hash72.value,
        render->frame_chain_hash216.value,
        style->styled_frame_chain_hash72.value,
        style->styled_frame_chain_hash216.value,
        style->palette_chain_hash72.value,
        style->palette_chain_hash216.value,
        style->timing_hash72.value,
        style->timing_hash216.value,
        render->final_game_receipt_hash72.value,
        render->final_game_state_hash216.value
    );
    return fclose(file) == 0;
}

static void hhs_usage(const char* program) {
    fprintf(stderr,
        "Usage: %s --text-file FILE --base-rgba FILE --styled-rgba FILE --pcm-output FILE --manifest FILE "
        "[--timing-file FILE] [--title TITLE] [--diagnostic-seconds N] [style options]\n",
        program);
}

int main(int argc, char** argv) {
    const char* text_path = hhs_argument_value(argc, argv, "--text-file");
    const char* base_rgba = hhs_argument_value(argc, argv, "--base-rgba");
    const char* styled_rgba = hhs_argument_value(argc, argv, "--styled-rgba");
    const char* pcm_path = hhs_argument_value(argc, argv, "--pcm-output");
    const char* manifest_path = hhs_argument_value(argc, argv, "--manifest");
    const char* timing_path = hhs_argument_value(argc, argv, "--timing-file");
    const char* title = hhs_argument_value(argc, argv, "--title");
    const char* diagnostic_seconds = hhs_argument_value(argc, argv, "--diagnostic-seconds");
    char* text = NULL;
    size_t text_length = 0U;
    size_t title_length;
    HHSStorybookReelConfig config;
    HHSStorybookReelStyleV2 style;
    HHSStorybookTimingSpanV2 timings[HHS_STORYBOOK_MAX_TIMING_SPANS];
    size_t timing_count = 0U;
    HHSStorybookReelReport render_report;
    HHSStorybookStyleReportV2 style_report;
    HHSStorybookReelStatus status;
    if (!text_path || !base_rgba || !styled_rgba || !pcm_path || !manifest_path) {
        hhs_usage(argv[0]);
        return 2;
    }
    if (!title) title = "HHS STORYBOOK";
    title_length = strlen(title);
    if (title_length > HHS_STORYBOOK_REEL_MAX_TITLE_BYTES) return 2;
    text = hhs_read_text(text_path, &text_length);
    if (!text || text_length == 0U) { free(text); return 2; }
    status = hhs_storybook_reel_default_config(&config);
    if (status != HHS_STORYBOOK_REEL_OK) { free(text); return 3; }
    if (diagnostic_seconds) {
        unsigned long seconds = hhs_parse_unsigned(diagnostic_seconds, HHS_STORYBOOK_REEL_DURATION_SECONDS);
        if (seconds == 0U || seconds > HHS_STORYBOOK_REEL_DURATION_SECONDS) { free(text); return 2; }
        config.frame_count = (uint32_t)(seconds * config.fps);
        config.scene_count = seconds < HHS_STORYBOOK_REEL_SCENES ? (uint32_t)seconds : HHS_STORYBOOK_REEL_SCENES;
        if (config.scene_count == 0U) config.scene_count = 1U;
    }
    status = hhs_storybook_style_default_v2(&style);
    if (status != HHS_STORYBOOK_REEL_OK) { free(text); return 3; }
    style.font_face = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--font-face"), style.font_face);
    style.font_effect = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--font-effect"), style.font_effect);
    style.font_scale = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--font-scale"), style.font_scale);
    style.letter_spacing = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--letter-spacing"), style.letter_spacing);
    style.effect_depth = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--effect-depth"), style.effect_depth);
    style.effect_speed = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--effect-speed"), style.effect_speed);
    style.effect_amplitude = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--effect-amplitude"), style.effect_amplitude);
    style.palette_mode = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--palette-mode"), style.palette_mode);
    style.phase_origin = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--phase-origin"), style.phase_origin);
    style.phase_scene_stride = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--phase-scene-stride"), style.phase_scene_stride);
    style.title_x = (int32_t)hhs_parse_signed(hhs_argument_value(argc, argv, "--title-x"), style.title_x);
    style.title_y = (int32_t)hhs_parse_signed(hhs_argument_value(argc, argv, "--title-y"), style.title_y);
    style.caption_x = (int32_t)hhs_parse_signed(hhs_argument_value(argc, argv, "--caption-x"), style.caption_x);
    style.caption_y = (int32_t)hhs_parse_signed(hhs_argument_value(argc, argv, "--caption-y"), style.caption_y);
    style.title_max_chars = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--title-max-chars"), style.title_max_chars);
    style.caption_chars_per_line = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--caption-chars-per-line"), style.caption_chars_per_line);
    style.caption_lines = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--caption-lines"), style.caption_lines);
    style.panel_opacity = (uint32_t)hhs_parse_unsigned(hhs_argument_value(argc, argv, "--panel-opacity"), style.panel_opacity);
    if (timing_path) {
        if (!hhs_read_timings(timing_path, timings, HHS_STORYBOOK_MAX_TIMING_SPANS, &timing_count)) { free(text); return 4; }
    } else if (!hhs_default_timings(text, text_length, &config, timings, HHS_STORYBOOK_MAX_TIMING_SPANS, &timing_count)) {
        free(text);
        return 4;
    }
    memset(&render_report, 0, sizeof(render_report));
    memset(&style_report, 0, sizeof(style_report));
    status = hhs_storybook_reel_render_files(text, text_length, title, title_length, &config, base_rgba, pcm_path, &render_report);
    if (status != HHS_STORYBOOK_REEL_OK) { free(text); return 5; }
    status = hhs_storybook_style_file_v2(base_rgba, styled_rgba, config.frame_count, title, title_length, text, text_length, timings, timing_count, &style, &style_report);
    if (status != HHS_STORYBOOK_REEL_OK) { free(text); return 6; }
    if (!hhs_write_manifest(manifest_path, &render_report, &style_report, &config, timing_count)) { free(text); return 7; }
    printf("{\"classification\":\"HHS_STORYBOOK_REEL_NATIVE_PIPELINE_VERIFIED\",\"manifest\":\"%s\",\"frames\":%u,\"parallel_computation_used\":false}\n", manifest_path, config.frame_count);
    free(text);
    return 0;
}
