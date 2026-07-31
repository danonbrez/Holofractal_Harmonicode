#ifndef HHS_STORYBOOK_REEL_H
#define HHS_STORYBOOK_REEL_H

#include <stddef.h>
#include <stdint.h>

#include "hhs_vm81_game_texture.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_STORYBOOK_REEL_ABI_VERSION 1U
#define HHS_STORYBOOK_REEL_WIDTH HHS_VM81_GAME_SCREEN_WIDTH
#define HHS_STORYBOOK_REEL_HEIGHT HHS_VM81_GAME_SCREEN_HEIGHT
#define HHS_STORYBOOK_REEL_CHANNELS 4U
#define HHS_STORYBOOK_REEL_RGBA_BYTES \
    ((size_t)HHS_STORYBOOK_REEL_WIDTH * (size_t)HHS_STORYBOOK_REEL_HEIGHT * HHS_STORYBOOK_REEL_CHANNELS)
#define HHS_STORYBOOK_REEL_FPS 30U
#define HHS_STORYBOOK_REEL_DURATION_SECONDS 90U
#define HHS_STORYBOOK_REEL_FRAME_COUNT \
    (HHS_STORYBOOK_REEL_FPS * HHS_STORYBOOK_REEL_DURATION_SECONDS)
#define HHS_STORYBOOK_REEL_AUDIO_RATE 48000U
#define HHS_STORYBOOK_REEL_AUDIO_CHANNELS 1U
#define HHS_STORYBOOK_REEL_SCENES 15U
#define HHS_STORYBOOK_REEL_MAX_TEXT_BYTES 16384U
#define HHS_STORYBOOK_REEL_MAX_TITLE_BYTES 128U
#define HHS_STORYBOOK_REEL_MAX_CAPTION_BYTES 96U
#define HHS_STORYBOOK_REEL_FULL_OPCODE_MASK ((1U << HHS_VM81_GAME_PROGRAM_LENGTH) - 1U)

typedef enum HHSStorybookReelStatus {
    HHS_STORYBOOK_REEL_OK = 0,
    HHS_STORYBOOK_REEL_INVALID_ARGUMENT = 1,
    HHS_STORYBOOK_REEL_TEXT_EMPTY = 2,
    HHS_STORYBOOK_REEL_TEXT_TOO_LARGE = 3,
    HHS_STORYBOOK_REEL_TITLE_TOO_LARGE = 4,
    HHS_STORYBOOK_REEL_FRAME_COUNT_INVALID = 5,
    HHS_STORYBOOK_REEL_IO_FAILURE = 6,
    HHS_STORYBOOK_REEL_GAME_ABI_FAILURE = 7,
    HHS_STORYBOOK_REEL_OPCODE_COVERAGE_FAILURE = 8,
    HHS_STORYBOOK_REEL_REPLAY_FAILURE = 9,
    HHS_STORYBOOK_REEL_PROGRAM_ROUNDTRIP_FAILURE = 10,
    HHS_STORYBOOK_REEL_STATE_MUTATION_FAILURE = 11
} HHSStorybookReelStatus;

typedef struct HHSStorybookReelConfig {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t fps;
    uint32_t frame_count;
    uint32_t audio_rate;
    uint32_t scene_count;
} HHSStorybookReelConfig;

typedef struct HHSStorybookScene {
    uint32_t index;
    uint32_t first_frame;
    uint32_t frame_count;
    uint32_t text_offset;
    uint32_t text_length;
    uint8_t palette[4];
    HHSHash72 scene_hash72;
    HHSHash216 scene_hash216;
} HHSStorybookScene;

typedef struct HHSStorybookReelReport {
    uint32_t status;
    uint32_t fps;
    uint32_t frame_count;
    uint32_t duration_seconds;
    uint32_t scene_count;
    uint32_t width;
    uint32_t height;
    uint32_t audio_rate;
    uint32_t audio_samples;
    uint32_t game_steps;
    uint32_t opcode_coverage;
    uint32_t receipts_emitted;
    uint32_t replay_verified;
    uint32_t program_roundtrip_verified;
    uint32_t state_projection_non_mutating;
    uint32_t parallel_computation_used;
    HHSHash72 story_hash72;
    HHSHash216 story_hash216;
    HHSHash72 frame_chain_hash72;
    HHSHash216 frame_chain_hash216;
    HHSHash72 final_game_receipt_hash72;
    HHSHash216 final_game_state_hash216;
} HHSStorybookReelReport;

const char* hhs_storybook_reel_status_name(HHSStorybookReelStatus status);

HHSStorybookReelStatus hhs_storybook_reel_default_config(
    HHSStorybookReelConfig* config
);

HHSStorybookReelStatus hhs_storybook_reel_plan_scenes(
    const char* text,
    size_t text_length,
    const HHSStorybookReelConfig* config,
    HHSStorybookScene* scenes,
    size_t scene_capacity
);

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
);

HHSStorybookReelStatus hhs_storybook_reel_render_files(
    const char* text,
    size_t text_length,
    const char* title,
    size_t title_length,
    const HHSStorybookReelConfig* config,
    const char* rgba_path,
    const char* pcm_path,
    HHSStorybookReelReport* report
);

#ifdef __cplusplus
}
#endif

#endif
