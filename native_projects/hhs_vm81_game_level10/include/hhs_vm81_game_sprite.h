#ifndef HHS_VM81_GAME_SPRITE_H
#define HHS_VM81_GAME_SPRITE_H

#include "hhs_vm81_game_release.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_VM81_GAME_SPRITE_WIDTH HHS_VM81_GAME_SCREEN_WIDTH
#define HHS_VM81_GAME_SPRITE_HEIGHT HHS_VM81_GAME_SCREEN_HEIGHT
#define HHS_VM81_GAME_SPRITE_CHANNELS 4U
#define HHS_VM81_GAME_SPRITE_RGBA_BYTES \
    ((size_t)HHS_VM81_GAME_SPRITE_WIDTH * (size_t)HHS_VM81_GAME_SPRITE_HEIGHT * HHS_VM81_GAME_SPRITE_CHANNELS)

#define HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE (1U << 0)
#define HHS_VM81_SPRITE_OVERLAY_PHASE      (1U << 1)
#define HHS_VM81_SPRITE_OVERLAY_GLOWS      (1U << 2)
#define HHS_VM81_SPRITE_OVERLAY_VIGNETTE   (1U << 3)
#define HHS_VM81_SPRITE_OVERLAY_HUD        (1U << 4)
#define HHS_VM81_SPRITE_OVERLAY_ALL        \
    (HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE | HHS_VM81_SPRITE_OVERLAY_PHASE | \
     HHS_VM81_SPRITE_OVERLAY_GLOWS | HHS_VM81_SPRITE_OVERLAY_VIGNETTE | \
     HHS_VM81_SPRITE_OVERLAY_HUD)

typedef struct HHSVM81GameSpriteReport {
    uint32_t width;
    uint32_t height;
    uint32_t overlay_flags;
    uint32_t unique_color_buckets;
    uint32_t nontransparent_pixels;
    uint32_t state_unchanged;
    HHSHash72 frame_hash72;
    HHSHash216 frame_hash216;
    HHSHash216 source_state_hash216;
} HHSVM81GameSpriteReport;

HHSVM81GameStatus hhs_vm81_game_sprite_render_rgba(
    const HHSVM81GameRelease* release,
    uint32_t overlay_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameSpriteReport* report
);

HHSVM81GameStatus hhs_vm81_game_sprite_write_ppm(
    const HHSVM81GameRelease* release,
    uint32_t overlay_flags,
    const char* path,
    HHSVM81GameSpriteReport* report
);

#ifdef __cplusplus
}
#endif

#endif
