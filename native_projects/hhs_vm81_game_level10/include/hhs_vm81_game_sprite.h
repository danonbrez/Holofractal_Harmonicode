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

/* Inherited gradient and interface overlays. Their meaning is frozen. */
#define HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE (1U << 0)
#define HHS_VM81_SPRITE_OVERLAY_PHASE      (1U << 1)
#define HHS_VM81_SPRITE_OVERLAY_GLOWS      (1U << 2)
#define HHS_VM81_SPRITE_OVERLAY_VIGNETTE   (1U << 3)
#define HHS_VM81_SPRITE_OVERLAY_HUD        (1U << 4)
#define HHS_VM81_SPRITE_OVERLAY_ALL        \
    (HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE | HHS_VM81_SPRITE_OVERLAY_PHASE | \
     HHS_VM81_SPRITE_OVERLAY_GLOWS | HHS_VM81_SPRITE_OVERLAY_VIGNETTE | \
     HHS_VM81_SPRITE_OVERLAY_HUD)

/* Additive governed texture layers. */
#define HHS_VM81_SPRITE_TEXTURE_FIELD       (1U << 5)
#define HHS_VM81_SPRITE_TEXTURE_MIDGROUND   (1U << 6)
#define HHS_VM81_SPRITE_TEXTURE_MATERIALS   (1U << 7)
#define HHS_VM81_SPRITE_TEXTURE_SEMANTIC    (1U << 8)
#define HHS_VM81_SPRITE_TEXTURE_PLAYER      (1U << 9)
#define HHS_VM81_SPRITE_TEXTURE_ALL         \
    (HHS_VM81_SPRITE_TEXTURE_FIELD | HHS_VM81_SPRITE_TEXTURE_MIDGROUND | \
     HHS_VM81_SPRITE_TEXTURE_MATERIALS | HHS_VM81_SPRITE_TEXTURE_SEMANTIC | \
     HHS_VM81_SPRITE_TEXTURE_PLAYER)

#define HHS_VM81_SPRITE_PRESENTATION_ALL \
    (HHS_VM81_SPRITE_OVERLAY_ALL | HHS_VM81_SPRITE_TEXTURE_ALL)
#define HHS_VM81_SPRITE_ALLOWED_FLAGS HHS_VM81_SPRITE_PRESENTATION_ALL

typedef struct HHSVM81GameSpriteReport {
    uint32_t width;
    uint32_t height;
    uint32_t overlay_flags;
    uint32_t texture_flags;
    uint32_t unique_color_buckets;
    uint32_t nontransparent_pixels;
    uint32_t texture_field_writes;
    uint32_t midground_writes;
    uint32_t material_writes;
    uint32_t semantic_writes;
    uint32_t player_texture_writes;
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
