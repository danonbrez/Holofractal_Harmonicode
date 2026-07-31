#ifndef HHS_STORYBOOK_REEL_STYLE_H
#define HHS_STORYBOOK_REEL_STYLE_H

#include "hhs_storybook_reel.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_STORYBOOK_STYLE_ABI_VERSION 1U
#define HHS_STORYBOOK_PHASE_AUTO 0xffffffffU
#define HHS_STORYBOOK_MAX_TIMING_SPANS HHS_STORYBOOK_REEL_SCENES

typedef enum HHSStorybookFontFace {
    HHS_STORYBOOK_FONT_CLASSIC = 0,
    HHS_STORYBOOK_FONT_BOLD = 1,
    HHS_STORYBOOK_FONT_SERIF = 2,
    HHS_STORYBOOK_FONT_WIDE = 3,
    HHS_STORYBOOK_FONT_SHADOW = 4
} HHSStorybookFontFace;

typedef enum HHSStorybookPaletteMode {
    HHS_STORYBOOK_PALETTE_RECIPROCAL_AUTO = 0,
    HHS_STORYBOOK_PALETTE_RECIPROCAL_FIXED = 1,
    HHS_STORYBOOK_PALETTE_MANUAL = 2
} HHSStorybookPaletteMode;

typedef struct HHSStorybookRGB {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} HHSStorybookRGB;

typedef struct HHSStorybookReciprocalPalette {
    uint8_t phase_x;
    uint8_t phase_y;
    uint8_t phase_z;
    uint8_t phase_w;
    HHSStorybookRGB x;
    HHSStorybookRGB y;
    HHSStorybookRGB z;
    HHSStorybookRGB w;
    HHSHash72 palette_hash72;
    HHSHash216 palette_hash216;
} HHSStorybookReciprocalPalette;

typedef struct HHSStorybookReelStyle {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t font_face;
    uint32_t font_scale;
    uint32_t letter_spacing;
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
    HHSStorybookRGB manual_x;
    HHSStorybookRGB manual_y;
    HHSStorybookRGB manual_z;
    HHSStorybookRGB manual_w;
} HHSStorybookReelStyle;

typedef struct HHSStorybookTimingSpan {
    uint32_t index;
    uint32_t first_frame;
    uint32_t frame_count;
    uint32_t text_offset;
    uint32_t text_length;
} HHSStorybookTimingSpan;

typedef struct HHSStorybookStyleReport {
    uint32_t frame_count;
    uint32_t timing_span_count;
    uint32_t font_face;
    uint32_t font_scale;
    uint32_t palette_mode;
    uint32_t phase_origin;
    uint32_t parallel_computation_used;
    HHSHash72 timing_hash72;
    HHSHash216 timing_hash216;
    HHSHash72 palette_chain_hash72;
    HHSHash216 palette_chain_hash216;
    HHSHash72 styled_frame_chain_hash72;
    HHSHash216 styled_frame_chain_hash216;
} HHSStorybookStyleReport;

HHSStorybookReelStatus hhs_storybook_style_default(
    HHSStorybookReelStyle* style
);

HHSStorybookReelStatus hhs_storybook_reciprocal_palette(
    const HHSHash216* story_hash216,
    uint32_t scene_index,
    const HHSStorybookReelStyle* style,
    HHSStorybookReciprocalPalette* palette
);

HHSStorybookReelStatus hhs_storybook_style_frame(
    uint8_t* rgba,
    size_t rgba_capacity,
    const char* title,
    size_t title_length,
    const char* text,
    size_t text_length,
    const HHSHash216* story_hash216,
    const HHSStorybookTimingSpan* timing,
    const HHSStorybookReelStyle* style,
    uint32_t frame_index,
    HHSStorybookReciprocalPalette* out_palette,
    HHSHash72* out_hash72,
    HHSHash216* out_hash216
);

HHSStorybookReelStatus hhs_storybook_style_file(
    const char* input_rgba_path,
    const char* output_rgba_path,
    uint32_t frame_count,
    const char* title,
    size_t title_length,
    const char* text,
    size_t text_length,
    const HHSStorybookTimingSpan* timings,
    size_t timing_count,
    const HHSStorybookReelStyle* style,
    HHSStorybookStyleReport* report
);

#ifdef __cplusplus
}
#endif

#endif
