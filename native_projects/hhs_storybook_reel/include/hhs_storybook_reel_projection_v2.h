#ifndef HHS_STORYBOOK_REEL_PROJECTION_V2_H
#define HHS_STORYBOOK_REEL_PROJECTION_V2_H

#include "hhs_storybook_reel.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_STORYBOOK_PROJECTION_ABI_VERSION 2U

typedef struct HHSStorybookProjectionConfigV2 {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t texture_flags;
    uint32_t sprite_overlay_flags;
} HHSStorybookProjectionConfigV2;

HHSStorybookReelStatus hhs_storybook_projection_default_v2(
    HHSStorybookProjectionConfigV2* config
);

HHSStorybookReelStatus hhs_storybook_projection_set_v2(
    const HHSStorybookProjectionConfigV2* config
);

HHSStorybookProjectionConfigV2 hhs_storybook_projection_current_v2(void);

HHSVM81GameStatus hhs_storybook_texture_render_bridge_v2(
    const HHSVM81GameRelease* release,
    uint32_t inherited_texture_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameTextureReport* report
);

#ifdef __cplusplus
}
#endif

#endif
