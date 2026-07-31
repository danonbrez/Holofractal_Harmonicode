#include "hhs_storybook_reel_style_v2.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HHS_STYLE_FONT_WIDTH 5
#define HHS_STYLE_FONT_HEIGHT 7
#define HHS_STYLE_MAX_LINE_CHARS 40U
#define HHS_STYLE_MAX_LINES 4U

static const uint8_t HHS_STYLE_FONT[37][HHS_STYLE_FONT_HEIGHT] = {
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

/* Twelve chromatic pitch classes mapped around a perceptual color wheel. */
static const HHSStorybookRGBV2 HHS_COLOR_WHEEL[HHS_STORYBOOK_CHROMATIC_TONES] = {
    {230U,65U,80U}, {235U,94U,55U}, {236U,132U,48U}, {229U,179U,45U},
    {181U,196U,47U}, {75U,174U,92U}, {44U,160U,151U}, {54U,128U,203U},
    {82U,92U,190U}, {137U,82U,186U}, {190U,71U,159U}, {218U,66U,117U}
};

/* x=tonic and z=tritone reciprocal. y/w select consonance or controlled chromatic tension. */
static const uint8_t HHS_HARMONIES[][4] = {
    {0U,4U,6U,7U}, {0U,3U,6U,7U}, {0U,5U,6U,7U}, {0U,3U,6U,9U},
    {0U,4U,6U,10U}, {0U,3U,6U,10U}, {0U,1U,6U,11U}, {0U,2U,6U,9U},
    {0U,4U,6U,11U}, {0U,5U,6U,10U}, {0U,2U,6U,8U}, {0U,1U,6U,7U}
};

static int hhs_style_validate(const HHSStorybookReelStyleV2* style) {
    if (!style || style->struct_size < sizeof(*style) || style->abi_version != HHS_STORYBOOK_STYLE_ABI_VERSION) return 0;
    if (style->font_face > HHS_STORYBOOK_FONT_SHADOW_V2 || style->font_effect > HHS_STORYBOOK_EFFECT_PHASE_WAVE_V2) return 0;
    if (style->font_scale < 1U || style->font_scale > 4U || style->letter_spacing > 8U) return 0;
    if (style->effect_depth > 12U || style->effect_speed == 0U || style->effect_speed > 72U || style->effect_amplitude > 24U) return 0;
    if (style->palette_mode > HHS_STORYBOOK_PALETTE_MANUAL_V2) return 0;
    if (style->phase_origin != HHS_STORYBOOK_PHASE_AUTO && style->phase_origin >= 72U) return 0;
    if (style->phase_scene_stride == 0U || style->phase_scene_stride >= 72U) return 0;
    if (style->title_max_chars == 0U || style->caption_chars_per_line == 0U || style->caption_chars_per_line > HHS_STYLE_MAX_LINE_CHARS) return 0;
    if (style->caption_lines == 0U || style->caption_lines > HHS_STYLE_MAX_LINES || style->panel_opacity > 255U) return 0;
    return 1;
}

static uint32_t hhs_style_seed(const HHSHash216* story_hash216, uint32_t scene_index) {
    uint32_t seed = 0x9e3779b9U ^ (scene_index * 0x85ebca6bU);
    size_t i;
    for (i = 0U; i < HHS_HASH216_LEN; ++i) {
        seed ^= (uint32_t)(unsigned char)story_hash216->value[i] + 0x9e3779b9U + (seed << 6U) + (seed >> 2U);
    }
    return seed == 0U ? 0xa341316cU : seed;
}

static uint32_t hhs_style_xorshift32(uint32_t* state) {
    uint32_t value = *state;
    value ^= value << 13U;
    value ^= value >> 17U;
    value ^= value << 5U;
    *state = value;
    return value;
}

static int hhs_style_triangle(uint32_t phase, uint32_t amplitude) {
    uint32_t p = phase % 72U;
    int value;
    if (p < 18U) value = (int)p;
    else if (p < 54U) value = 36 - (int)p;
    else value = (int)p - 72;
    return (value * (int)amplitude) / 18;
}

static HHSStorybookRGBV2 hhs_style_mix(HHSStorybookRGBV2 a, HHSStorybookRGBV2 b, uint32_t b_weight) {
    HHSStorybookRGBV2 out;
    uint32_t a_weight = 100U - b_weight;
    out.r = (uint8_t)(((uint32_t)a.r * a_weight + (uint32_t)b.r * b_weight) / 100U);
    out.g = (uint8_t)(((uint32_t)a.g * a_weight + (uint32_t)b.g * b_weight) / 100U);
    out.b = (uint8_t)(((uint32_t)a.b * a_weight + (uint32_t)b.b * b_weight) / 100U);
    return out;
}

static void hhs_style_blend(uint8_t* rgba, int x, int y, HHSStorybookRGBV2 color, uint8_t alpha) {
    size_t offset;
    uint32_t inverse;
    if (!rgba || x < 0 || y < 0 || x >= HHS_STORYBOOK_REEL_WIDTH || y >= HHS_STORYBOOK_REEL_HEIGHT) return;
    offset = ((size_t)y * HHS_STORYBOOK_REEL_WIDTH + (size_t)x) * HHS_STORYBOOK_REEL_CHANNELS;
    inverse = 255U - alpha;
    rgba[offset + 0U] = (uint8_t)(((uint32_t)rgba[offset + 0U] * inverse + (uint32_t)color.r * alpha) / 255U);
    rgba[offset + 1U] = (uint8_t)(((uint32_t)rgba[offset + 1U] * inverse + (uint32_t)color.g * alpha) / 255U);
    rgba[offset + 2U] = (uint8_t)(((uint32_t)rgba[offset + 2U] * inverse + (uint32_t)color.b * alpha) / 255U);
    rgba[offset + 3U] = 255U;
}

static void hhs_style_fill(uint8_t* rgba, int x, int y, int width, int height, HHSStorybookRGBV2 color, uint8_t alpha) {
    int py;
    int px;
    for (py = y; py < y + height; ++py) {
        for (px = x; px < x + width; ++px) hhs_style_blend(rgba, px, py, color, alpha);
    }
}

static int hhs_style_font_index(char c) {
    unsigned char value = (unsigned char)c;
    if (value >= 'a' && value <= 'z') value = (unsigned char)(value - 'a' + 'A');
    if (value >= 'A' && value <= 'Z') return (int)(value - 'A');
    if (value >= '0' && value <= '9') return 26 + (int)(value - '0');
    return value == ' ' ? 36 : -1;
}

static void hhs_style_block(
    uint8_t* rgba,
    int x,
    int y,
    uint32_t scale,
    HHSStorybookRGBV2 color,
    uint8_t alpha
) {
    uint32_t sy;
    uint32_t sx;
    for (sy = 0U; sy < scale; ++sy) {
        for (sx = 0U; sx < scale; ++sx) hhs_style_blend(rgba, x + (int)sx, y + (int)sy, color, alpha);
    }
}

static void hhs_style_char(
    uint8_t* rgba,
    int x,
    int y,
    char c,
    const HHSStorybookReelStyleV2* style,
    const HHSStorybookReciprocalPaletteV2* palette,
    uint32_t frame_index,
    uint32_t glyph_index
) {
    int index = hhs_style_font_index(c);
    int row;
    int column;
    uint32_t layer;
    int phase_x = 0;
    int phase_y = 0;
    uint32_t phase = (frame_index * style->effect_speed + glyph_index * 6U) % 72U;
    if (index < 0) index = 36;
    if (style->font_effect == HHS_STORYBOOK_EFFECT_PARALLAX_V2) {
        phase_x = hhs_style_triangle(phase, style->effect_amplitude);
        phase_y = hhs_style_triangle((phase + 18U) % 72U, style->effect_amplitude / 2U + 1U);
    } else if (style->font_effect == HHS_STORYBOOK_EFFECT_ORBITAL_V2) {
        phase_x = hhs_style_triangle(phase, style->effect_amplitude);
        phase_y = hhs_style_triangle((phase + 18U) % 72U, style->effect_amplitude);
    } else if (style->font_effect == HHS_STORYBOOK_EFFECT_PHASE_WAVE_V2) {
        phase_y = hhs_style_triangle(phase, style->effect_amplitude);
    }
    if (style->font_effect != HHS_STORYBOOK_EFFECT_FLAT_V2) {
        uint32_t depth = style->effect_depth == 0U ? 1U : style->effect_depth;
        for (layer = depth; layer > 0U; --layer) {
            HHSStorybookRGBV2 extrusion = hhs_style_mix(palette->z, palette->w, (layer * 70U) / depth);
            for (row = 0; row < HHS_STYLE_FONT_HEIGHT; ++row) {
                uint8_t bits = HHS_STYLE_FONT[index][row];
                for (column = 0; column < HHS_STYLE_FONT_WIDTH; ++column) {
                    if ((bits & (uint8_t)(1U << (HHS_STYLE_FONT_WIDTH - 1 - column))) != 0U) {
                        int px = x + phase_x + column * (int)style->font_scale + (int)layer;
                        int py = y + phase_y + row * (int)style->font_scale + (int)layer;
                        hhs_style_block(rgba, px, py, style->font_scale, extrusion, 175U);
                    }
                }
            }
        }
    }
    for (row = 0; row < HHS_STYLE_FONT_HEIGHT; ++row) {
        uint8_t bits = HHS_STYLE_FONT[index][row];
        for (column = 0; column < HHS_STYLE_FONT_WIDTH; ++column) {
            if ((bits & (uint8_t)(1U << (HHS_STYLE_FONT_WIDTH - 1 - column))) != 0U) {
                int horizontal_scale = style->font_face == HHS_STORYBOOK_FONT_WIDE_V2 ? (int)style->font_scale + 1 : (int)style->font_scale;
                int px = x + phase_x + column * horizontal_scale;
                int py = y + phase_y + row * (int)style->font_scale;
                if (style->font_face == HHS_STORYBOOK_FONT_SHADOW_V2) {
                    HHSStorybookRGBV2 shadow = {10U,8U,14U};
                    hhs_style_block(rgba, px + 1, py + 1, style->font_scale, shadow, 190U);
                }
                hhs_style_block(rgba, px, py, style->font_scale, palette->y, 255U);
                if (style->font_face == HHS_STORYBOOK_FONT_BOLD_V2) {
                    hhs_style_block(rgba, px + 1, py, style->font_scale, palette->y, 230U);
                }
            }
        }
    }
    if (style->font_face == HHS_STORYBOOK_FONT_SERIF_V2 && index != 36) {
        int width = HHS_STYLE_FONT_WIDTH * (int)style->font_scale;
        hhs_style_fill(rgba, x + phase_x, y + phase_y, width, (int)style->font_scale, palette->w, 210U);
        hhs_style_fill(rgba, x + phase_x, y + phase_y + HHS_STYLE_FONT_HEIGHT * (int)style->font_scale - 1, width, (int)style->font_scale, palette->w, 210U);
    }
}

static int hhs_style_advance(const HHSStorybookReelStyleV2* style) {
    uint32_t width = style->font_face == HHS_STORYBOOK_FONT_WIDE_V2 ? 6U : 5U;
    return (int)(width * style->font_scale + style->letter_spacing);
}

static void hhs_style_text(
    uint8_t* rgba,
    int x,
    int y,
    const char* text,
    size_t length,
    size_t max_chars,
    const HHSStorybookReelStyleV2* style,
    const HHSStorybookReciprocalPaletteV2* palette,
    uint32_t frame_index
) {
    size_t i;
    size_t count = length < max_chars ? length : max_chars;
    int cursor = x;
    int advance = hhs_style_advance(style);
    for (i = 0U; i < count; ++i) {
        char c = text[i];
        if (c == '\n' || c == '\r' || c == '\t') c = ' ';
        hhs_style_char(rgba, cursor, y, c, style, palette, frame_index, (uint32_t)i);
        cursor += advance;
    }
}

static size_t hhs_style_caption(
    const char* text,
    size_t text_length,
    const HHSStorybookTimingSpanV2* timing,
    char* out,
    size_t capacity
) {
    size_t source;
    size_t end;
    size_t target = 0U;
    int previous_space = 1;
    if (!text || !timing || !out || capacity == 0U) return 0U;
    source = timing->text_offset < text_length ? timing->text_offset : text_length;
    end = source + timing->text_length;
    if (end > text_length) end = text_length;
    while (source < end && target + 1U < capacity) {
        unsigned char c = (unsigned char)text[source++];
        if (isspace(c) || c < 32U || c > 126U) {
            if (!previous_space) out[target++] = ' ';
            previous_space = 1;
        } else {
            out[target++] = (char)toupper(c);
            previous_space = 0;
        }
    }
    while (target > 0U && out[target - 1U] == ' ') target--;
    out[target] = '\0';
    return target;
}

static const HHSStorybookTimingSpanV2* hhs_style_timing_for_frame(
    const HHSStorybookTimingSpanV2* timings,
    size_t timing_count,
    uint32_t frame_index
) {
    size_t i;
    for (i = 0U; i < timing_count; ++i) {
        uint32_t end = timings[i].first_frame + timings[i].frame_count;
        if (frame_index >= timings[i].first_frame && frame_index < end) return &timings[i];
    }
    return timing_count > 0U ? &timings[timing_count - 1U] : NULL;
}

HHSStorybookReelStatus hhs_storybook_style_default_v2(HHSStorybookReelStyleV2* style) {
    if (!style) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(style, 0, sizeof(*style));
    style->struct_size = (uint32_t)sizeof(*style);
    style->abi_version = HHS_STORYBOOK_STYLE_ABI_VERSION;
    style->font_face = HHS_STORYBOOK_FONT_SHADOW_V2;
    style->font_effect = HHS_STORYBOOK_EFFECT_EXTRUDED_V2;
    style->font_scale = 1U;
    style->letter_spacing = 1U;
    style->effect_depth = 3U;
    style->effect_speed = 1U;
    style->effect_amplitude = 3U;
    style->palette_mode = HHS_STORYBOOK_PALETTE_RECIPROCAL_AUTO_V2;
    style->phase_origin = HHS_STORYBOOK_PHASE_AUTO;
    style->phase_scene_stride = 6U;
    style->title_x = 12;
    style->title_y = 12;
    style->caption_x = 12;
    style->caption_y = 106;
    style->title_max_chars = 20U;
    style->caption_chars_per_line = 22U;
    style->caption_lines = 2U;
    style->panel_opacity = 214U;
    style->manual_x = HHS_COLOR_WHEEL[0];
    style->manual_y = HHS_COLOR_WHEEL[4];
    style->manual_z = HHS_COLOR_WHEEL[6];
    style->manual_w = HHS_COLOR_WHEEL[7];
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_reciprocal_palette_v2(
    const HHSHash216* story_hash216,
    uint32_t scene_index,
    const HHSStorybookReelStyleV2* style,
    HHSStorybookReciprocalPaletteV2* palette
) {
    uint32_t seed;
    uint32_t harmony_index;
    uint32_t tonic;
    uint8_t canonical[18];
    if (!story_hash216 || !palette || !hhs_style_validate(style)) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(palette, 0, sizeof(*palette));
    if (style->palette_mode == HHS_STORYBOOK_PALETTE_MANUAL_V2) {
        palette->chromatic_tonic = 0U;
        palette->harmony_class = 0U;
        palette->phase_x = 0U;
        palette->phase_y = 24U;
        palette->phase_z = HHS_STORYBOOK_RECIPROCAL_PHASE_OFFSET;
        palette->phase_w = 42U;
        palette->x = style->manual_x;
        palette->y = style->manual_y;
        palette->z = style->manual_z;
        palette->w = style->manual_w;
    } else {
        seed = hhs_style_seed(story_hash216, scene_index);
        harmony_index = hhs_style_xorshift32(&seed) % (sizeof(HHS_HARMONIES) / sizeof(HHS_HARMONIES[0]));
        if (style->palette_mode == HHS_STORYBOOK_PALETTE_RECIPROCAL_FIXED_V2 && style->phase_origin != HHS_STORYBOOK_PHASE_AUTO) {
            tonic = (style->phase_origin / HHS_STORYBOOK_PHASES_PER_TONE) % HHS_STORYBOOK_CHROMATIC_TONES;
        } else {
            uint32_t stride = style->phase_scene_stride / HHS_STORYBOOK_PHASES_PER_TONE + 1U;
            tonic = (hhs_style_xorshift32(&seed) + scene_index * stride) % HHS_STORYBOOK_CHROMATIC_TONES;
        }
        palette->chromatic_tonic = (uint8_t)tonic;
        palette->harmony_class = (uint8_t)harmony_index;
        palette->phase_x = (uint8_t)(tonic * HHS_STORYBOOK_PHASES_PER_TONE);
        palette->phase_y = (uint8_t)(((tonic + HHS_HARMONIES[harmony_index][1]) % HHS_STORYBOOK_CHROMATIC_TONES) * HHS_STORYBOOK_PHASES_PER_TONE);
        palette->phase_z = (uint8_t)((palette->phase_x + HHS_STORYBOOK_RECIPROCAL_PHASE_OFFSET) % 72U);
        palette->phase_w = (uint8_t)(((tonic + HHS_HARMONIES[harmony_index][3]) % HHS_STORYBOOK_CHROMATIC_TONES) * HHS_STORYBOOK_PHASES_PER_TONE);
        palette->x = HHS_COLOR_WHEEL[tonic];
        palette->y = HHS_COLOR_WHEEL[(tonic + HHS_HARMONIES[harmony_index][1]) % HHS_STORYBOOK_CHROMATIC_TONES];
        palette->z = HHS_COLOR_WHEEL[(tonic + 6U) % HHS_STORYBOOK_CHROMATIC_TONES];
        palette->w = HHS_COLOR_WHEEL[(tonic + HHS_HARMONIES[harmony_index][3]) % HHS_STORYBOOK_CHROMATIC_TONES];
        if ((hhs_style_xorshift32(&seed) & 1U) != 0U) {
            palette->y = hhs_style_mix(palette->y, palette->z, 24U + scene_index % 25U);
            palette->w = hhs_style_mix(palette->w, palette->x, 18U + scene_index % 31U);
        }
    }
    canonical[0] = palette->chromatic_tonic;
    canonical[1] = palette->harmony_class;
    canonical[2] = palette->phase_x;
    canonical[3] = palette->phase_y;
    canonical[4] = palette->phase_z;
    canonical[5] = palette->phase_w;
    canonical[6] = palette->x.r; canonical[7] = palette->x.g; canonical[8] = palette->x.b;
    canonical[9] = palette->y.r; canonical[10] = palette->y.g; canonical[11] = palette->y.b;
    canonical[12] = palette->z.r; canonical[13] = palette->z.g; canonical[14] = palette->z.b;
    canonical[15] = palette->w.r; canonical[16] = palette->w.g; canonical[17] = palette->w.b;
    hhs_hash72_compute(canonical, sizeof(canonical), &palette->palette_hash72);
    hhs_hash216_compute(canonical, sizeof(canonical), &palette->palette_hash216);
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_style_frame_v2(
    uint8_t* rgba,
    size_t rgba_capacity,
    const char* title,
    size_t title_length,
    const char* text,
    size_t text_length,
    const HHSHash216* story_hash216,
    const HHSStorybookTimingSpanV2* timing,
    const HHSStorybookReelStyleV2* style,
    uint32_t frame_index,
    HHSStorybookReciprocalPaletteV2* out_palette,
    HHSHash72* out_hash72,
    HHSHash216* out_hash216
) {
    char caption[HHS_STORYBOOK_REEL_MAX_CAPTION_BYTES * 3U];
    size_t caption_length;
    size_t source = 0U;
    uint32_t line;
    uint32_t progress;
    int title_height;
    int caption_height;
    if (!rgba || rgba_capacity < HHS_STORYBOOK_REEL_RGBA_BYTES || !title || !text || !story_hash216 || !timing || !out_palette || !out_hash72 || !out_hash216 || !hhs_style_validate(style)) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    if (hhs_storybook_reciprocal_palette_v2(story_hash216, timing->index, style, out_palette) != HHS_STORYBOOK_REEL_OK) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    title_height = (int)(HHS_STYLE_FONT_HEIGHT * style->font_scale + style->effect_depth + 7U);
    caption_height = (int)(style->caption_lines * (HHS_STYLE_FONT_HEIGHT * style->font_scale + style->effect_depth + 3U) + 7U);
    hhs_style_fill(rgba, style->title_x - 4, style->title_y - 4, 152 - style->title_x, title_height, out_palette->x, (uint8_t)style->panel_opacity);
    hhs_style_fill(rgba, style->caption_x - 4, style->caption_y - 4, 152 - style->caption_x, caption_height, out_palette->z, (uint8_t)style->panel_opacity);
    hhs_style_fill(rgba, 3, 3, 3, 138, out_palette->x, 220U);
    hhs_style_fill(rgba, 154, 3, 3, 138, out_palette->z, 220U);
    hhs_style_fill(rgba, 6, 3, 148, 2, out_palette->y, 220U);
    hhs_style_fill(rgba, 6, 139, 148, 2, out_palette->w, 220U);
    hhs_style_text(rgba, style->title_x, style->title_y, title, title_length, style->title_max_chars, style, out_palette, frame_index);
    caption_length = hhs_style_caption(text, text_length, timing, caption, sizeof(caption));
    for (line = 0U; line < style->caption_lines && source < caption_length; ++line) {
        size_t remaining = caption_length - source;
        size_t count = remaining < style->caption_chars_per_line ? remaining : style->caption_chars_per_line;
        int line_y = style->caption_y + (int)(line * (HHS_STYLE_FONT_HEIGHT * style->font_scale + style->effect_depth + 3U));
        hhs_style_text(rgba, style->caption_x, line_y, caption + source, count, count, style, out_palette, frame_index);
        source += count;
        while (source < caption_length && caption[source] == ' ') source++;
    }
    progress = timing->frame_count ? ((frame_index - timing->first_frame) * 138U) / timing->frame_count : 0U;
    if (progress > 138U) progress = 138U;
    hhs_style_fill(rgba, 11, 135, (int)progress, 2, out_palette->w, 255U);
    hhs_hash72_compute(rgba, HHS_STORYBOOK_REEL_RGBA_BYTES, out_hash72);
    hhs_hash216_compute(rgba, HHS_STORYBOOK_REEL_RGBA_BYTES, out_hash216);
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_style_file_v2(
    const char* input_rgba_path,
    const char* output_rgba_path,
    uint32_t frame_count,
    const char* title,
    size_t title_length,
    const char* text,
    size_t text_length,
    const HHSStorybookTimingSpanV2* timings,
    size_t timing_count,
    const HHSStorybookReelStyleV2* style,
    HHSStorybookStyleReportV2* report
) {
    FILE* input = NULL;
    FILE* output = NULL;
    uint8_t* rgba = NULL;
    HHSHash216 story_hash216;
    HHSHash72 palette_chain72;
    HHSHash216 palette_chain216;
    HHSHash72 frame_chain72;
    HHSHash216 frame_chain216;
    HHSStorybookReciprocalPaletteV2 palette;
    HHSHash72 frame_hash72;
    HHSHash216 frame_hash216;
    uint32_t frame_index;
    char chain[512];
    int written;
    HHSStorybookReelStatus status = HHS_STORYBOOK_REEL_OK;
    if (!input_rgba_path || !output_rgba_path || !title || !text || !timings || timing_count == 0U || !report || !hhs_style_validate(style)) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(report, 0, sizeof(*report));
    input = fopen(input_rgba_path, "rb");
    output = fopen(output_rgba_path, "wb");
    rgba = (uint8_t*)malloc(HHS_STORYBOOK_REEL_RGBA_BYTES);
    if (!input || !output || !rgba) {
        status = HHS_STORYBOOK_REEL_IO_FAILURE;
        goto finish;
    }
    hhs_hash216_compute(text, text_length, &story_hash216);
    hhs_hash72_compute(timings, timing_count * sizeof(*timings), &report->timing_hash72);
    hhs_hash216_compute(timings, timing_count * sizeof(*timings), &report->timing_hash216);
    palette_chain72 = report->timing_hash72;
    palette_chain216 = report->timing_hash216;
    frame_chain72 = report->timing_hash72;
    frame_chain216 = report->timing_hash216;
    for (frame_index = 0U; frame_index < frame_count; ++frame_index) {
        const HHSStorybookTimingSpanV2* timing = hhs_style_timing_for_frame(timings, timing_count, frame_index);
        if (!timing || fread(rgba, 1U, HHS_STORYBOOK_REEL_RGBA_BYTES, input) != HHS_STORYBOOK_REEL_RGBA_BYTES) {
            status = HHS_STORYBOOK_REEL_IO_FAILURE;
            goto finish;
        }
        status = hhs_storybook_style_frame_v2(rgba, HHS_STORYBOOK_REEL_RGBA_BYTES, title, title_length, text, text_length, &story_hash216, timing, style, frame_index, &palette, &frame_hash72, &frame_hash216);
        if (status != HHS_STORYBOOK_REEL_OK) goto finish;
        if (fwrite(rgba, 1U, HHS_STORYBOOK_REEL_RGBA_BYTES, output) != HHS_STORYBOOK_REEL_RGBA_BYTES) {
            status = HHS_STORYBOOK_REEL_IO_FAILURE;
            goto finish;
        }
        written = snprintf(chain, sizeof(chain), "%s|%s|%u", palette_chain72.value, palette.palette_hash72.value, frame_index);
        if (written <= 0 || (size_t)written >= sizeof(chain)) { status = HHS_STORYBOOK_REEL_IO_FAILURE; goto finish; }
        hhs_hash72_compute(chain, (size_t)written, &palette_chain72);
        written = snprintf(chain, sizeof(chain), "%s|%s|%u", palette_chain216.value, palette.palette_hash216.value, frame_index);
        if (written <= 0 || (size_t)written >= sizeof(chain)) { status = HHS_STORYBOOK_REEL_IO_FAILURE; goto finish; }
        hhs_hash216_compute(chain, (size_t)written, &palette_chain216);
        written = snprintf(chain, sizeof(chain), "%s|%s|%u", frame_chain72.value, frame_hash72.value, frame_index);
        if (written <= 0 || (size_t)written >= sizeof(chain)) { status = HHS_STORYBOOK_REEL_IO_FAILURE; goto finish; }
        hhs_hash72_compute(chain, (size_t)written, &frame_chain72);
        written = snprintf(chain, sizeof(chain), "%s|%s|%u", frame_chain216.value, frame_hash216.value, frame_index);
        if (written <= 0 || (size_t)written >= sizeof(chain)) { status = HHS_STORYBOOK_REEL_IO_FAILURE; goto finish; }
        hhs_hash216_compute(chain, (size_t)written, &frame_chain216);
    }
    report->frame_count = frame_count;
    report->timing_span_count = (uint32_t)timing_count;
    report->font_face = style->font_face;
    report->font_effect = style->font_effect;
    report->font_scale = style->font_scale;
    report->palette_mode = style->palette_mode;
    report->phase_origin = style->phase_origin;
    report->reciprocal_phase_offset = HHS_STORYBOOK_RECIPROCAL_PHASE_OFFSET;
    report->chromatic_tones = HHS_STORYBOOK_CHROMATIC_TONES;
    report->parallel_computation_used = 0U;
    report->palette_chain_hash72 = palette_chain72;
    report->palette_chain_hash216 = palette_chain216;
    report->styled_frame_chain_hash72 = frame_chain72;
    report->styled_frame_chain_hash216 = frame_chain216;
finish:
    if (input && fclose(input) != 0 && status == HHS_STORYBOOK_REEL_OK) status = HHS_STORYBOOK_REEL_IO_FAILURE;
    if (output && fclose(output) != 0 && status == HHS_STORYBOOK_REEL_OK) status = HHS_STORYBOOK_REEL_IO_FAILURE;
    free(rgba);
    return status;
}
