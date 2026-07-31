#include "hhs_storybook_reel.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HHS_STORYBOOK_FONT_WIDTH 5
#define HHS_STORYBOOK_FONT_HEIGHT 7
#define HHS_STORYBOOK_CAPTION_CHARS 48U
#define HHS_STORYBOOK_CHAIN_BYTES (HHS_HASH72_LEN * 2U + sizeof(uint32_t))

static const uint8_t HHS_STORYBOOK_FONT[37][HHS_STORYBOOK_FONT_HEIGHT] = {
    {14,17,17,31,17,17,17}, {30,17,17,30,17,17,30}, {14,17,16,16,16,17,14},
    {30,17,17,17,17,17,30}, {31,16,16,30,16,16,31}, {31,16,16,30,16,16,16},
    {14,17,16,23,17,17,15}, {17,17,17,31,17,17,17}, {14,4,4,4,4,4,14},
    {7,2,2,2,18,18,12}, {17,18,20,24,20,18,17}, {16,16,16,16,16,16,31},
    {17,27,21,21,17,17,17}, {17,25,21,19,17,17,17}, {14,17,17,17,17,17,14},
    {30,17,17,30,16,16,16}, {14,17,17,17,21,18,13}, {30,17,17,30,20,18,17},
    {15,16,16,14,1,1,30}, {31,4,4,4,4,4,4}, {17,17,17,17,17,17,14},
    {17,17,17,17,17,10,4}, {17,17,17,21,21,21,10}, {17,17,10,4,10,17,17},
    {17,17,10,4,4,4,4}, {31,1,2,4,8,16,31},
    {14,17,19,21,25,17,14}, {4,12,4,4,4,4,14}, {14,17,1,2,4,8,31},
    {30,1,1,14,1,1,30}, {2,6,10,18,31,2,2}, {31,16,30,1,1,17,14},
    {6,8,16,30,17,17,14}, {31,1,2,4,8,8,8}, {14,17,17,14,17,17,14},
    {14,17,17,15,1,2,12}, {0,0,0,0,0,0,0}
};

static size_t hhs_storybook_bounded_strlen(const char* value, size_t limit) {
    size_t n = 0U;
    if (!value) return 0U;
    while (n < limit && value[n] != '\0') n++;
    return n;
}

static uint8_t hhs_storybook_hash_byte(const char* value, size_t index) {
    unsigned char c = (unsigned char)value[index];
    return (uint8_t)((c * 37U + (unsigned char)index * 17U) & 0xffU);
}

static void hhs_storybook_set_pixel(uint8_t* rgba, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    size_t offset;
    if (!rgba || x < 0 || y < 0 || x >= HHS_STORYBOOK_REEL_WIDTH || y >= HHS_STORYBOOK_REEL_HEIGHT) return;
    offset = ((size_t)y * HHS_STORYBOOK_REEL_WIDTH + (size_t)x) * HHS_STORYBOOK_REEL_CHANNELS;
    rgba[offset + 0U] = r;
    rgba[offset + 1U] = g;
    rgba[offset + 2U] = b;
    rgba[offset + 3U] = a;
}

static void hhs_storybook_blend_pixel(uint8_t* rgba, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t alpha) {
    size_t offset;
    uint32_t inverse;
    if (!rgba || x < 0 || y < 0 || x >= HHS_STORYBOOK_REEL_WIDTH || y >= HHS_STORYBOOK_REEL_HEIGHT) return;
    offset = ((size_t)y * HHS_STORYBOOK_REEL_WIDTH + (size_t)x) * HHS_STORYBOOK_REEL_CHANNELS;
    inverse = 255U - alpha;
    rgba[offset + 0U] = (uint8_t)(((uint32_t)rgba[offset + 0U] * inverse + (uint32_t)r * alpha) / 255U);
    rgba[offset + 1U] = (uint8_t)(((uint32_t)rgba[offset + 1U] * inverse + (uint32_t)g * alpha) / 255U);
    rgba[offset + 2U] = (uint8_t)(((uint32_t)rgba[offset + 2U] * inverse + (uint32_t)b * alpha) / 255U);
    rgba[offset + 3U] = 255U;
}

static void hhs_storybook_fill_rect(uint8_t* rgba, int x, int y, int w, int h, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    int py;
    int px;
    for (py = y; py < y + h; ++py) {
        for (px = x; px < x + w; ++px) hhs_storybook_blend_pixel(rgba, px, py, r, g, b, a);
    }
}

static void hhs_storybook_draw_rect(uint8_t* rgba, int x, int y, int w, int h, uint8_t r, uint8_t g, uint8_t b) {
    int i;
    for (i = 0; i < w; ++i) {
        hhs_storybook_set_pixel(rgba, x + i, y, r, g, b, 255U);
        hhs_storybook_set_pixel(rgba, x + i, y + h - 1, r, g, b, 255U);
    }
    for (i = 0; i < h; ++i) {
        hhs_storybook_set_pixel(rgba, x, y + i, r, g, b, 255U);
        hhs_storybook_set_pixel(rgba, x + w - 1, y + i, r, g, b, 255U);
    }
}

static void hhs_storybook_fill_circle(uint8_t* rgba, int cx, int cy, int radius, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    int y;
    int x;
    int radius_squared = radius * radius;
    for (y = -radius; y <= radius; ++y) {
        for (x = -radius; x <= radius; ++x) {
            if (x * x + y * y <= radius_squared) hhs_storybook_blend_pixel(rgba, cx + x, cy + y, r, g, b, a);
        }
    }
}

static int hhs_storybook_font_index(char c) {
    unsigned char uc = (unsigned char)c;
    if (uc >= 'a' && uc <= 'z') uc = (unsigned char)(uc - 'a' + 'A');
    if (uc >= 'A' && uc <= 'Z') return (int)(uc - 'A');
    if (uc >= '0' && uc <= '9') return 26 + (int)(uc - '0');
    if (uc == ' ') return 36;
    return -1;
}

static void hhs_storybook_draw_char(uint8_t* rgba, int x, int y, char c, uint8_t r, uint8_t g, uint8_t b) {
    int index = hhs_storybook_font_index(c);
    int row;
    int column;
    if (index < 0) {
        hhs_storybook_draw_rect(rgba, x, y, HHS_STORYBOOK_FONT_WIDTH, HHS_STORYBOOK_FONT_HEIGHT, r, g, b);
        return;
    }
    for (row = 0; row < HHS_STORYBOOK_FONT_HEIGHT; ++row) {
        uint8_t bits = HHS_STORYBOOK_FONT[index][row];
        for (column = 0; column < HHS_STORYBOOK_FONT_WIDTH; ++column) {
            if ((bits & (uint8_t)(1U << (HHS_STORYBOOK_FONT_WIDTH - 1 - column))) != 0U) {
                hhs_storybook_set_pixel(rgba, x + column, y + row, r, g, b, 255U);
            }
        }
    }
}

static void hhs_storybook_draw_text(uint8_t* rgba, int x, int y, const char* text, size_t length, size_t max_chars, uint8_t r, uint8_t g, uint8_t b) {
    size_t i;
    size_t count = length < max_chars ? length : max_chars;
    int cursor = x;
    for (i = 0U; i < count; ++i) {
        char c = text[i];
        if (c == '\n' || c == '\r') c = ' ';
        hhs_storybook_draw_char(rgba, cursor, y, c, r, g, b);
        cursor += HHS_STORYBOOK_FONT_WIDTH + 1;
    }
}

static void hhs_storybook_caption(const char* text, const HHSStorybookScene* scene, char* out, size_t capacity) {
    size_t source = scene->text_offset;
    size_t end = source + scene->text_length;
    size_t target = 0U;
    int previous_space = 1;
    if (!out || capacity == 0U) return;
    while (source < end && target + 1U < capacity && target < HHS_STORYBOOK_CAPTION_CHARS) {
        unsigned char c = (unsigned char)text[source++];
        if (isspace(c)) {
            if (!previous_space) out[target++] = ' ';
            previous_space = 1;
        } else if (c < 32U || c > 126U) {
            if (!previous_space) out[target++] = ' ';
            previous_space = 1;
        } else {
            out[target++] = (char)toupper(c);
            previous_space = 0;
        }
    }
    while (target > 0U && out[target - 1U] == ' ') target--;
    out[target] = '\0';
}

static void hhs_storybook_apply_page(uint8_t* rgba, const HHSStorybookScene* scene, uint32_t local_frame, const char* title, size_t title_length, const char* text) {
    size_t pixels = (size_t)HHS_STORYBOOK_REEL_WIDTH * HHS_STORYBOOK_REEL_HEIGHT;
    size_t i;
    uint8_t tint_r = (uint8_t)(64U + scene->palette[0] / 2U);
    uint8_t tint_g = (uint8_t)(48U + scene->palette[1] / 2U);
    uint8_t tint_b = (uint8_t)(56U + scene->palette[2] / 2U);
    uint8_t ink_r = (uint8_t)(230U - scene->palette[0] / 5U);
    uint8_t ink_g = (uint8_t)(220U - scene->palette[1] / 6U);
    uint8_t ink_b = (uint8_t)(205U - scene->palette[2] / 7U);
    int drift = (int)((local_frame / 3U + scene->index * 7U) % 21U) - 10;
    char caption[HHS_STORYBOOK_REEL_MAX_CAPTION_BYTES];
    for (i = 0U; i < pixels; ++i) {
        size_t offset = i * HHS_STORYBOOK_REEL_CHANNELS;
        rgba[offset + 0U] = (uint8_t)(((uint32_t)rgba[offset + 0U] * 180U + (uint32_t)tint_r * 75U) / 255U);
        rgba[offset + 1U] = (uint8_t)(((uint32_t)rgba[offset + 1U] * 180U + (uint32_t)tint_g * 75U) / 255U);
        rgba[offset + 2U] = (uint8_t)(((uint32_t)rgba[offset + 2U] * 180U + (uint32_t)tint_b * 75U) / 255U);
        rgba[offset + 3U] = 255U;
    }
    hhs_storybook_fill_rect(rgba, 4, 4, 152, 136, 244U, 225U, 193U, 38U);
    hhs_storybook_draw_rect(rgba, 4, 4, 152, 136, ink_r, ink_g, ink_b);
    hhs_storybook_draw_rect(rgba, 7, 7, 146, 130, tint_r, tint_g, tint_b);

    hhs_storybook_fill_circle(rgba, 38 + drift, 58, 17, scene->palette[0], scene->palette[1], scene->palette[2], 188U);
    hhs_storybook_fill_circle(rgba, 84 - drift / 2, 49 + drift / 3, 12, scene->palette[2], scene->palette[0], scene->palette[1], 170U);
    hhs_storybook_fill_circle(rgba, 123 + drift / 2, 66 - drift / 4, 15, scene->palette[1], scene->palette[2], scene->palette[0], 184U);
    hhs_storybook_fill_rect(rgba, 26 + drift, 69, 24, 24, scene->palette[2], scene->palette[1], scene->palette[0], 150U);
    hhs_storybook_fill_rect(rgba, 105 - drift, 76, 30, 16, scene->palette[0], scene->palette[2], scene->palette[1], 145U);

    if (scene->index == 0U && title && title_length > 0U) {
        hhs_storybook_fill_rect(rgba, 12, 11, 136, 12, 24U, 18U, 20U, 176U);
        hhs_storybook_draw_text(rgba, 15, 13, title, title_length, 22U, 250U, 232U, 188U);
    } else {
        char scene_label[24];
        int written = snprintf(scene_label, sizeof(scene_label), "PAGE %02u OF %02u", scene->index + 1U, HHS_STORYBOOK_REEL_SCENES);
        if (written > 0) hhs_storybook_draw_text(rgba, 15, 13, scene_label, (size_t)written, 22U, 250U, 232U, 188U);
    }

    hhs_storybook_caption(text, scene, caption, sizeof(caption));
    hhs_storybook_fill_rect(rgba, 10, 101, 140, 32, 18U, 14U, 18U, 205U);
    hhs_storybook_draw_text(rgba, 13, 105, caption, strlen(caption), 23U, 248U, 231U, 198U);
    if (strlen(caption) > 23U) {
        hhs_storybook_draw_text(rgba, 13, 114, caption + 23U, strlen(caption + 23U), 23U, 248U, 231U, 198U);
    }
    hhs_storybook_draw_text(rgba, 13, 124, "HHS VM81 STORYBOOK", 18U, 18U, 207U, 173U, 118U);
}

static HHSStorybookReelStatus hhs_storybook_validate_config(const HHSStorybookReelConfig* config) {
    if (!config || config->struct_size < sizeof(*config) || config->abi_version != HHS_STORYBOOK_REEL_ABI_VERSION) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    if (config->fps == 0U || config->frame_count == 0U || config->frame_count % config->fps != 0U) return HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID;
    if (config->scene_count == 0U || config->scene_count > HHS_STORYBOOK_REEL_SCENES) return HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID;
    if (config->audio_rate == 0U) return HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID;
    return HHS_STORYBOOK_REEL_OK;
}

const char* hhs_storybook_reel_status_name(HHSStorybookReelStatus status) {
    switch (status) {
        case HHS_STORYBOOK_REEL_OK: return "HHS_STORYBOOK_REEL_OK";
        case HHS_STORYBOOK_REEL_INVALID_ARGUMENT: return "HHS_STORYBOOK_REEL_INVALID_ARGUMENT";
        case HHS_STORYBOOK_REEL_TEXT_EMPTY: return "HHS_STORYBOOK_REEL_TEXT_EMPTY";
        case HHS_STORYBOOK_REEL_TEXT_TOO_LARGE: return "HHS_STORYBOOK_REEL_TEXT_TOO_LARGE";
        case HHS_STORYBOOK_REEL_TITLE_TOO_LARGE: return "HHS_STORYBOOK_REEL_TITLE_TOO_LARGE";
        case HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID: return "HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID";
        case HHS_STORYBOOK_REEL_IO_FAILURE: return "HHS_STORYBOOK_REEL_IO_FAILURE";
        case HHS_STORYBOOK_REEL_GAME_ABI_FAILURE: return "HHS_STORYBOOK_REEL_GAME_ABI_FAILURE";
        case HHS_STORYBOOK_REEL_OPCODE_COVERAGE_FAILURE: return "HHS_STORYBOOK_REEL_OPCODE_COVERAGE_FAILURE";
        case HHS_STORYBOOK_REEL_REPLAY_FAILURE: return "HHS_STORYBOOK_REEL_REPLAY_FAILURE";
        case HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE: return "HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE";
        case HHS_STORYBOOK_REEL_STATE_MUTATION_FAILURE: return "HHS_STORYBOOK_REEL_STATE_MUTATION_FAILURE";
        default: return "HHS_STORYBOOK_REEL_UNKNOWN";
    }
}

HHSStorybookReelStatus hhs_storybook_reel_default_config(HHSStorybookReelConfig* config) {
    if (!config) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(config, 0, sizeof(*config));
    config->struct_size = (uint32_t)sizeof(*config);
    config->abi_version = HHS_STORYBOOK_REEL_ABI_VERSION;
    config->fps = HHS_STORYBOOK_REEL_FPS;
    config->frame_count = HHS_STORYBOOK_REEL_FRAME_COUNT;
    config->audio_rate = HHS_STORYBOOK_REEL_AUDIO_RATE;
    config->scene_count = HHS_STORYBOOK_REEL_SCENES;
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_reel_plan_scenes(
    const char* text,
    size_t text_length,
    const HHSStorybookReelConfig* config,
    HHSStorybookScene* scenes,
    size_t scene_capacity
) {
    uint32_t scene_index;
    size_t cursor = 0U;
    HHSStorybookReelStatus config_status = hhs_storybook_validate_config(config);
    if (config_status != HHS_STORYBOOK_REEL_OK) return config_status;
    if (!text || !scenes || scene_capacity < config->scene_count) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    if (text_length == 0U) return HHS_STORYBOOK_REEL_TEXT_EMPTY;
    if (text_length > HHS_STORYBOOK_REEL_MAX_TEXT_BYTES) return HHS_STORYBOOK_REEL_TEXT_TOO_LARGE;

    for (scene_index = 0U; scene_index < config->scene_count; ++scene_index) {
        size_t remaining = text_length - cursor;
        size_t remaining_scenes = (size_t)config->scene_count - scene_index;
        size_t target = scene_index + 1U == config->scene_count ? text_length : cursor + remaining / remaining_scenes;
        size_t end = target;
        size_t search_limit;
        size_t p;
        HHSStorybookScene* scene = &scenes[scene_index];
        if (scene_index + 1U != config->scene_count) {
            search_limit = target + 80U < text_length ? target + 80U : text_length;
            for (p = target; p < search_limit; ++p) {
                if (text[p] == '.' || text[p] == '!' || text[p] == '?' || text[p] == '\n') {
                    end = p + 1U;
                    break;
                }
            }
            if (end == target) {
                p = target;
                while (p > cursor + 1U) {
                    if (isspace((unsigned char)text[p - 1U])) {
                        end = p;
                        break;
                    }
                    p--;
                }
            }
        }
        if (end <= cursor) end = cursor + 1U;
        if (end > text_length) end = text_length;
        memset(scene, 0, sizeof(*scene));
        scene->index = scene_index;
        scene->first_frame = (uint32_t)(((uint64_t)config->frame_count * scene_index) / config->scene_count);
        scene->frame_count = (uint32_t)(((uint64_t)config->frame_count * (scene_index + 1U)) / config->scene_count) - scene->first_frame;
        scene->text_offset = (uint32_t)cursor;
        scene->text_length = (uint32_t)(end - cursor);
        hhs_hash72_compute(text + cursor, end - cursor, &scene->scene_hash72);
        hhs_hash216_compute(text + cursor, end - cursor, &scene->scene_hash216);
        scene->palette[0] = (uint8_t)(48U + hhs_storybook_hash_byte(scene->scene_hash216.value, 3U) % 176U);
        scene->palette[1] = (uint8_t)(48U + hhs_storybook_hash_byte(scene->scene_hash216.value, 83U) % 176U);
        scene->palette[2] = (uint8_t)(48U + hhs_storybook_hash_byte(scene->scene_hash216.value, 163U) % 176U);
        scene->palette[3] = 255U;
        cursor = end;
    }
    return HHS_STORYBOOK_REEL_OK;
}

static const HHSStorybookScene* hhs_storybook_scene_for_frame(const HHSStorybookScene* scenes, size_t scene_count, uint32_t frame_index) {
    size_t i;
    for (i = 0U; i < scene_count; ++i) {
        uint32_t end = scenes[i].first_frame + scenes[i].frame_count;
        if (frame_index >= scenes[i].first_frame && frame_index < end) return &scenes[i];
    }
    return scene_count > 0U ? &scenes[scene_count - 1U] : NULL;
}

HHSStorybookReelStatus hhs_storybook_reel_render_frame(
    const char* text,
    size_t text_length,
    const char* title,
    size_t title_length,
    const HHSStorybookReelConfig* config,
    const HHSStorybookScene* scenes,
    size_t scene_count,
    uint32_t frame_index,
    HHSVM81GameRelease* release,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSHash72* out_frame_hash72,
    HHSHash216* out_frame_hash216
) {
    const HHSStorybookScene* scene;
    uint32_t local_frame;
    uint8_t input = 0U;
    HHSVM81GameStatus game_status;
    HHSVM81GameTextureReport texture_report;
    HHSHash216 state_before;
    HHSStorybookReelStatus config_status = hhs_storybook_validate_config(config);
    (void)text_length;
    if (config_status != HHS_STORYBOOK_REEL_OK) return config_status;
    if (!text || !title || !scenes || !release || !out_rgba || !out_frame_hash72 || !out_frame_hash216) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    if (out_capacity < HHS_STORYBOOK_REEL_RGBA_BYTES || frame_index >= config->frame_count) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    scene = hhs_storybook_scene_for_frame(scenes, scene_count, frame_index);
    if (!scene) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    local_frame = frame_index - scene->first_frame;

    if (frame_index == 0U) {
        game_status = hhs_vm81_game_release_init(release);
        if (game_status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
        game_status = hhs_vm81_game_release_start(release);
        if (game_status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
    } else if (local_frame == 0U || release->phase != HHS_GAME_RELEASE_RUNNING) {
        game_status = hhs_vm81_game_release_restart(release);
        if (game_status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
    }

    if (((local_frame / 45U) & 1U) == 0U) input |= HHS_VM81_GAME_INPUT_RIGHT;
    else input |= HHS_VM81_GAME_INPUT_LEFT;
    if (((local_frame + scene->palette[0]) % 53U) == 0U) input |= HHS_VM81_GAME_INPUT_JUMP;
    game_status = hhs_vm81_game_release_step(release, input);
    if (game_status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;

    state_before = release->vm.latest_state_identity_hash216;
    memset(&texture_report, 0, sizeof(texture_report));
    game_status = hhs_vm81_game_texture_render_rgba(
        release,
        HHS_VM81_TEXTURE_ALL,
        out_rgba,
        out_capacity,
        &texture_report
    );
    if (game_status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
    if (!texture_report.state_unchanged || !hhs_hash216_equal(&state_before, &release->vm.latest_state_identity_hash216)) {
        return HHS_STORYBOOK_REEL_STATE_MUTATION_FAILURE;
    }
    hhs_storybook_apply_page(out_rgba, scene, local_frame, title, title_length, text);
    hhs_hash72_compute(out_rgba, HHS_STORYBOOK_REEL_RGBA_BYTES, out_frame_hash72);
    hhs_hash216_compute(out_rgba, HHS_STORYBOOK_REEL_RGBA_BYTES, out_frame_hash216);
    return HHS_STORYBOOK_REEL_OK;
}

static HHSStorybookReelStatus hhs_storybook_verify_full_game_abi(HHSStorybookReelReport* report) {
    HHSVM81GameRelease verification;
    HHSVM81GameReleaseReport expected;
    HHSVM81GameReleaseReport replay;
    HHSVM81GameStatus status;
    char encoded[256];
    uint8_t decoded[HHS_VM81_GAME_PROGRAM_LENGTH];
    size_t decoded_length = 0U;
    size_t i;
    status = hhs_vm81_game_release_init(&verification);
    if (status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
    status = hhs_vm81_game_release_run_headless(&verification, &expected);
    if (status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_GAME_ABI_FAILURE;
    if (expected.opcode_coverage != HHS_STORYBOOK_REEL_FULL_OPCODE_MASK) return HHS_STORYBOOK_REEL_OPCODE_COVERAGE_FAILURE;
    status = hhs_vm81_game_release_replay_verify(&verification, &replay);
    if (status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_REPLAY_FAILURE;
    status = hhs_vm81_game_base20_encode_program(verification.vm.program, HHS_VM81_GAME_PROGRAM_LENGTH, encoded, sizeof(encoded));
    if (status != HHS_GAME_STATUS_OK) return HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE;
    status = hhs_vm81_game_base20_decode_program(encoded, decoded, sizeof(decoded), &decoded_length);
    if (status != HHS_GAME_STATUS_OK || decoded_length != HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE;
    for (i = 0U; i < decoded_length; ++i) {
        if (decoded[i] != verification.vm.program[i].opcode_digit) return HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE;
    }
    report->opcode_coverage = expected.opcode_coverage;
    report->receipts_emitted = expected.receipts_emitted;
    report->replay_verified = 1U;
    report->program_roundtrip_verified = 1U;
    report->final_game_receipt_hash72 = expected.final_receipt_hash72;
    report->final_game_state_hash216 = expected.final_state_identity_hash216;
    return HHS_STORYBOOK_REEL_OK;
}

static HHSStorybookReelStatus hhs_storybook_write_audio(
    FILE* pcm,
    const HHSStorybookReelConfig* config,
    const HHSStorybookScene* scenes,
    size_t scene_count,
    uint32_t* out_samples
) {
    uint64_t total_samples = ((uint64_t)config->frame_count * config->audio_rate) / config->fps;
    uint64_t sample_index;
    uint32_t phase_a = 0U;
    uint32_t phase_b = 0U;
    if (total_samples > 0xffffffffULL) return HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID;
    for (sample_index = 0U; sample_index < total_samples; ++sample_index) {
        uint32_t frame_index = (uint32_t)((sample_index * config->fps) / config->audio_rate);
        const HHSStorybookScene* scene = hhs_storybook_scene_for_frame(scenes, scene_count, frame_index);
        uint32_t frequency_a = 180U + (uint32_t)(scene->palette[0] % 240U);
        uint32_t frequency_b = 270U + (uint32_t)(scene->palette[1] % 360U);
        uint32_t step_a = (uint32_t)(((uint64_t)frequency_a << 16U) / config->audio_rate);
        uint32_t step_b = (uint32_t)(((uint64_t)frequency_b << 16U) / config->audio_rate);
        uint32_t wave_a;
        uint32_t wave_b;
        int32_t signed_a;
        int32_t signed_b;
        int32_t envelope;
        int32_t mixed;
        int16_t sample;
        phase_a += step_a;
        phase_b += step_b;
        wave_a = phase_a & 0xffffU;
        wave_b = phase_b & 0xffffU;
        wave_a = wave_a < 32768U ? wave_a : 65535U - wave_a;
        wave_b = wave_b < 32768U ? wave_b : 65535U - wave_b;
        signed_a = (int32_t)wave_a * 2 - 32767;
        signed_b = (int32_t)wave_b * 2 - 32767;
        envelope = 5000 - (int32_t)((sample_index % (config->audio_rate * 6U)) / 24U);
        if (envelope < 1800) envelope = 1800;
        mixed = (signed_a * envelope) / 32767 + (signed_b * (envelope / 2)) / 32767;
        if (mixed > 32767) mixed = 32767;
        if (mixed < -32768) mixed = -32768;
        sample = (int16_t)mixed;
        if (fwrite(&sample, sizeof(sample), 1U, pcm) != 1U) return HHS_STORYBOOK_REEL_IO_FAILURE;
    }
    *out_samples = (uint32_t)total_samples;
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_reel_render_files(
    const char* text,
    size_t text_length,
    const char* title,
    size_t title_length,
    const HHSStorybookReelConfig* config,
    const char* rgba_path,
    const char* pcm_path,
    HHSStorybookReelReport* report
) {
    HHSStorybookScene scenes[HHS_STORYBOOK_REEL_SCENES];
    HHSVM81GameRelease release;
    uint8_t* rgba = NULL;
    FILE* rgba_file = NULL;
    FILE* pcm_file = NULL;
    HHSStorybookReelStatus status;
    uint32_t frame_index;
    uint32_t prior_instructions = 0U;
    HHSHash72 frame_hash72;
    HHSHash216 frame_hash216;
    HHSHash72 chain72;
    HHSHash216 chain216;
    char chain_buffer[HHS_HASH216_LEN * 2U + 32U];
    if (!report) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(report, 0, sizeof(*report));
    status = hhs_storybook_validate_config(config);
    if (status != HHS_STORYBOOK_REEL_OK) goto finish;
    if (!text || !title || !rgba_path || !pcm_path) {
        status = HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
        goto finish;
    }
    if (text_length == 0U) {
        status = HHS_STORYBOOK_REEL_TEXT_EMPTY;
        goto finish;
    }
    if (text_length > HHS_STORYBOOK_REEL_MAX_TEXT_BYTES) {
        status = HHS_STORYBOOK_REEL_TEXT_TOO_LARGE;
        goto finish;
    }
    if (title_length > HHS_STORYBOOK_REEL_MAX_TITLE_BYTES) {
        status = HHS_STORYBOOK_REEL_TITLE_TOO_LARGE;
        goto finish;
    }
    status = hhs_storybook_verify_full_game_abi(report);
    if (status != HHS_STORYBOOK_REEL_OK) goto finish;
    status = hhs_storybook_reel_plan_scenes(text, text_length, config, scenes, HHS_STORYBOOK_REEL_SCENES);
    if (status != HHS_STORYBOOK_REEL_OK) goto finish;

    hhs_hash72_compute(text, text_length, &report->story_hash72);
    hhs_hash216_compute(text, text_length, &report->story_hash216);
    chain72 = report->story_hash72;
    chain216 = report->story_hash216;
    rgba = (uint8_t*)malloc(HHS_STORYBOOK_REEL_RGBA_BYTES);
    if (!rgba) {
        status = HHS_STORYBOOK_REEL_IO_FAILURE;
        goto finish;
    }
    rgba_file = fopen(rgba_path, "wb");
    pcm_file = fopen(pcm_path, "wb");
    if (!rgba_file || !pcm_file) {
        status = HHS_STORYBOOK_REEL_IO_FAILURE;
        goto finish;
    }
    memset(&release, 0, sizeof(release));
    report->state_projection_non_mutating = 1U;
    for (frame_index = 0U; frame_index < config->frame_count; ++frame_index) {
        uint32_t before = release.instructions_executed;
        int written;
        status = hhs_storybook_reel_render_frame(
            text,
            text_length,
            title,
            title_length,
            config,
            scenes,
            config->scene_count,
            frame_index,
            &release,
            rgba,
            HHS_STORYBOOK_REEL_RGBA_BYTES,
            &frame_hash72,
            &frame_hash216
        );
        if (status != HHS_STORYBOOK_REEL_OK) goto finish;
        if (fwrite(rgba, 1U, HHS_STORYBOOK_REEL_RGBA_BYTES, rgba_file) != HHS_STORYBOOK_REEL_RGBA_BYTES) {
            status = HHS_STORYBOOK_REEL_IO_FAILURE;
            goto finish;
        }
        if (release.instructions_executed >= before) report->game_steps += release.instructions_executed - before;
        else report->game_steps += release.instructions_executed;
        prior_instructions = release.instructions_executed;
        (void)prior_instructions;
        written = snprintf(
            chain_buffer,
            sizeof(chain_buffer),
            "%s|%s|%u",
            chain72.value,
            frame_hash72.value,
            frame_index
        );
        if (written <= 0 || (size_t)written >= sizeof(chain_buffer)) {
            status = HHS_STORYBOOK_REEL_IO_FAILURE;
            goto finish;
        }
        hhs_hash72_compute(chain_buffer, (size_t)written, &chain72);
        written = snprintf(
            chain_buffer,
            sizeof(chain_buffer),
            "%s|%s|%u",
            chain216.value,
            frame_hash216.value,
            frame_index
        );
        if (written <= 0 || (size_t)written >= sizeof(chain_buffer)) {
            status = HHS_STORYBOOK_REEL_IO_FAILURE;
            goto finish;
        }
        hhs_hash216_compute(chain_buffer, (size_t)written, &chain216);
    }
    status = hhs_storybook_write_audio(pcm_file, config, scenes, config->scene_count, &report->audio_samples);
    if (status != HHS_STORYBOOK_REEL_OK) goto finish;
    report->frame_chain_hash72 = chain72;
    report->frame_chain_hash216 = chain216;
    report->fps = config->fps;
    report->frame_count = config->frame_count;
    report->duration_seconds = config->frame_count / config->fps;
    report->scene_count = config->scene_count;
    report->width = HHS_STORYBOOK_REEL_WIDTH;
    report->height = HHS_STORYBOOK_REEL_HEIGHT;
    report->audio_rate = config->audio_rate;
    report->parallel_computation_used = 0U;
    status = HHS_STORYBOOK_REEL_OK;

finish:
    if (rgba_file && fclose(rgba_file) != 0 && status == HHS_STORYBOOK_REEL_OK) status = HHS_STORYBOOK_REEL_IO_FAILURE;
    if (pcm_file && fclose(pcm_file) != 0 && status == HHS_STORYBOOK_REEL_OK) status = HHS_STORYBOOK_REEL_IO_FAILURE;
    free(rgba);
    report->status = (uint32_t)status;
    return status;
}
