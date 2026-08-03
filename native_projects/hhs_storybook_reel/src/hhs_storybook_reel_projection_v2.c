#include "hhs_storybook_reel_projection_v2.h"

#include <string.h>

static HHSStorybookProjectionConfigV2 HHS_STORYBOOK_PROJECTION_V2 = {
    sizeof(HHSStorybookProjectionConfigV2),
    HHS_STORYBOOK_PROJECTION_ABI_VERSION,
    HHS_VM81_TEXTURE_ALL,
    HHS_VM81_SPRITE_OVERLAY_ALL
};

static HHSVM81GameStatus hhs_storybook_sprite_render_bridge_v2(
    const HHSVM81GameRelease* release,
    uint32_t inherited_overlay_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameSpriteReport* report
) {
    (void)inherited_overlay_flags;
    return hhs_vm81_game_sprite_render_rgba(
        release,
        HHS_STORYBOOK_PROJECTION_V2.sprite_overlay_flags,
        out_rgba,
        out_capacity,
        report
    );
}

#define hhs_vm81_game_sprite_render_rgba hhs_storybook_sprite_render_bridge_v2
#define hhs_vm81_game_texture_render_rgba hhs_storybook_texture_render_base_v2
#define hhs_vm81_game_texture_write_ppm hhs_storybook_texture_write_ppm_base_v2
#include "hhs_vm81_game_texture.c"
#undef hhs_vm81_game_texture_write_ppm
#undef hhs_vm81_game_texture_render_rgba
#undef hhs_vm81_game_sprite_render_rgba

HHSStorybookReelStatus hhs_storybook_projection_default_v2(
    HHSStorybookProjectionConfigV2* config
) {
    if (!config) return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    memset(config, 0, sizeof(*config));
    config->struct_size = sizeof(*config);
    config->abi_version = HHS_STORYBOOK_PROJECTION_ABI_VERSION;
    config->texture_flags = HHS_VM81_TEXTURE_ALL;
    config->sprite_overlay_flags = HHS_VM81_SPRITE_OVERLAY_ALL;
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookReelStatus hhs_storybook_projection_set_v2(
    const HHSStorybookProjectionConfigV2* config
) {
    if (!config || config->struct_size < sizeof(*config) ||
        config->abi_version != HHS_STORYBOOK_PROJECTION_ABI_VERSION) {
        return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    }
    if ((config->texture_flags & ~HHS_VM81_TEXTURE_ALL) != 0U ||
        (config->sprite_overlay_flags & ~HHS_VM81_SPRITE_OVERLAY_ALL) != 0U) {
        return HHS_STORYBOOK_REEL_INVALID_ARGUMENT;
    }
    HHS_STORYBOOK_PROJECTION_V2 = *config;
    return HHS_STORYBOOK_REEL_OK;
}

HHSStorybookProjectionConfigV2 hhs_storybook_projection_current_v2(void) {
    return HHS_STORYBOOK_PROJECTION_V2;
}

HHSVM81GameStatus hhs_storybook_texture_render_bridge_v2(
    const HHSVM81GameRelease* release,
    uint32_t inherited_texture_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameTextureReport* report
) {
    (void)inherited_texture_flags;
    return hhs_storybook_texture_render_base_v2(
        release,
        HHS_STORYBOOK_PROJECTION_V2.texture_flags,
        out_rgba,
        out_capacity,
        report
    );
}
