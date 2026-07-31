#ifndef HHS_STORYBOOK_REEL_STYLE_V2_H
#define HHS_STORYBOOK_REEL_STYLE_V2_H

#include "hhs_storybook_reel.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_STORYBOOK_STYLE_ABI_VERSION 2U
#define HHS_STORYBOOK_PHASE_AUTO 0xffffffffU
#define HHS_STORYBOOK_MAX_TIMING_SPANS 256U
#define HHS_STORYBOOK_CHROMATIC_TONES 12U
#define HHS_STORYBOOK_PHASES_PER_TONE 6U
#define HHS_STORYBOOK_RECIPROCAL_PHASE_OFFSET 36U

typedef enum HHSStorybookFontFaceV2 {
    HHS_STORYBOOK_FONT_CLASSIC_V2 = 0,
    HHS_STORYBOOK_FONT_BOLD_V2 = 1,
    HHS_STORYBOOK_FONT_SERIF_V2 = 2,
    HHS_STORYBOOK_FONT_WIDE_V2 = 3,
    HHS_STORYBOOK_FONT_SHADOW_V2 = 4
} HHSStorybookFontFaceV2;

typedef enum HHSStorybookFontEffectV2 {
    HHS_STORYBOOK_EFFECT_FLAT_V2 = 0,
    HHS_STORYBOOK_EFFECT_EXTRUDED_V2 = 1,
    HHS_STORYBOOK_EFFECT_PARALLAX_V2 = 2,
    HHS_STORYBOOK_EFFECT_ORBITAL_V2 = 3,
    HHS_STORYBOOK_EFFECT_PHASE_WAVE_V2 = 4
} HHSStorybookFontEffectV2;

typedef enum HHSStorybookPaletteModeV2 {
    HHS_STORYBOOK_PALETTE_RECIPROCAL_AUTO_V2 = 0,
    HHS_STORYBOOK_PALETTE_RECIPROCAL_FIXED_V2 = 1,
    HHS_STORYBOOK_PALETTE_MANUAL_V2 = 2
} HHSStorybookPaletteModeV2;

typedef struct HHSStorybookRGBV2 {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} HHSStorybookRGBV2;

typedef struct HHSStorybookReciprocalPaletteV2 {
    uint8_t chromatic_tonic;
    uint8_t harmony_class;
    uint8_t phase_x;
    uint8_t phase_y;
    uint8_t phase_z;
    uint8_t phase_w;
    HHSStorybookRGBV2 x;
    HHSStorybookRGBV2 y;
    HHSStorybookRGBV2 z;
    HHSStorybookRGBV2 w;
    HHSHash72 palette_hash72;
    HHSHash216 palette_hash216;
} HHSStorybookReciprocalPaletteV2;

typedef struct HHSStorybookReelStyleV2 {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t font_face;
    uint32_t font_effect;
    uint32_t font_scale;
    uint32_t letter_spacing;
    uint32_t effect_depth;
    uint32_t effect_speed;
    uint32_t effect_amplitude;
    uint32_t palette_mode;
    uint32_t phase_origin;
    uint32_t phase_scene_stride;
    int32_t title_x;
    int32_t title_y;
    int32_t caption_x;
    int32_t caption_y;
    uint32_t title_max_chars;
    uint32_t caption_chars_per_line;
    uint32_t caption_lines;
    uint32_t panel_opacity;
    HHSStorybookRGBV2 manual_x;
    HHSStorybookRGBV2 manual_y;
    HHSStorybookRGBV2 manual_z;
    HHSStorybookRGBV2 manual_w;
} HHSStorybookReelStyleV2;

typedef struct HHSStorybookTimingSpanV2 {
    uint32_t index;
    uint32_t first_frame;
    uint32_t frame_count;
    uint32_t text_offset;
    uint32_t text_length;
} HHSStorybookTimingSpanV2;

typedef struct HHSStorybookStyleReportV2 {
    uint32_t frame_count;
    uint32_t timing_span_count;
    uint32_t font_face;
    uint32_t font_effect;
    uint32_t font_scale;
    uint32_t palette_mode;
    uint32_t phase_origin;
    uint32_t reciprocal_phase_offset;
    uint32_t chromatic_tones;
    uint32_t parallel_computation_used;
    HHSHash72 timing_hash72;
    HHSHash216 timing_hash216;
    HHSHash72 palette_chain_hash72;
    HHSHash216 palette_chain_hash216;
    HHSHash72 styled_frame_chain_hash72;
    HHSHash216 styled_frame_chain_hash216;
} HHSStorybookStyleReportV2;

HHSStorybookReelStatus hhs_storybook_style_default_v2(HHSStorybookReelStyleV2* style);
HHSStorybookReelStatus hhs_storybook_reciprocal_palette_v2(
    const HHSHash216* story_hash216,
    uint32_t scene_index,
    const HHSStorybookReelStyleV2* style,
    HHSStorybookReciprocalPaletteV2* palette
);
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
);
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
);

#ifdef __cplusplus
}
#endif

#endif
